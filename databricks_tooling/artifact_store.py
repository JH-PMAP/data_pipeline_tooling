import os
import subprocess
import io
import uuid
from azure.storage.blob import BlobServiceClient
import sys
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings

# This library takes these docs:
# https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-directory-file-acl-python
# and puts them into library form.
# There is no new information here of any kind, it is just a clean up of the above docs.
# The above docs show some examples of how to use the datalake client, I then went to the
# full rest api and implemented more pieces of that for greater functionality in python.
# There are no new features here.
# full rest api: https://docs.microsoft.com/en-us/python/api/azure-storage-file-datalake/azure.storage.filedatalake?view=azure-python

# This works on Continuous Deployment generically
# other solutions the author found only work on databricks notebooks

class AzureDataLakeClient:
    def __init__(self, storage_account_name, file_system_name, storage_account_key='', client_id='', client_secret='', tenant_id=''):
        self.storage_account_name = storage_account_name
        if storage_account_key != '':
            
            self.service_client = self.initialize_storage_account(
                storage_account_name,
                storage_account_key
            )
        elif client_id != '':
            self.service_client = self.initialize_storage_account_ad(
                storage_account_name,
                client_id,
                client_secret,
                tenant_id
            )
        self.file_system_client = self.get_or_create_file_system(
            file_system_name
        )
        
    def initialize_storage_account(self, storage_account_name, storage_account_key):
        try:  
            return DataLakeServiceClient(
                account_url=f"https://{storage_account_name}.dfs.core.windows.net",
                credential=storage_account_key
            )

        except Exception as e:
            raise e

    def initialize_storage_account_ad(self, storage_account_name, client_id, client_secret, tenant_id):
        try:  
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            return DataLakeServiceClient(
                account_url=f"https://{storage_account_name}.dfs.core.windows.net",
                credential=credential
            )

        except Exception as e:
            raise e

    def get_or_create_file_system(self, file_system_name):
        try:
            try:
                return self.service_client.create_file_system(
                    file_system=file_system_name
                )
            except:
                return self.service_client.get_file_system_client(
                    file_system=file_system_name
                )
        except Exception as e:
            raise e

    def create_directory(self, directory_name):
        try:
            self.file_system_client.create_directory(
                directory_name
            )
        except Exception as e:
            raise e

    def rename_directory(self, dir_name, new_dir_name):
        try:
            dir_client = self.file_system_client.get_directory_client(
                dir_name
            )
            new_dir_path = dir_client.file_system_name + "/" + new_dir_name
            dir_client.rename_directory(new_name=new_dir_path)
        except Exception as e:
            raise e
        
    def delete_directory(self, dir_name):
        try:
            dir_client = self.file_system_client.get_directory_client(dir_name)
            dir_client.delete_directory()
        except Exception as e:
            raise e

    def upload_file(self, local_file_path, remote_file_path):
        try:
            file_client = self.get_file_client(remote_file_path)
            with open(local_file_path) as local_file:
                contents = local_file.read()
                
            file_client.append_data(
                data=contents,
                offset=0,
                length=len(contents)
            )
            file_client.flush_data(len(contents))
        except Exception as e:
            raise e

    def get_file_client(self, remote_file_path):
        try:
            remote_file = remote_file_path.split("/")[-1]
            remote_dir = "/".join(remote_file_path.split("/")[:-1])
            dir_client = self.file_system_client.get_directory_client(remote_dir)
            return dir_client.create_file(remote_file)
        except Exception as e:
            raise e

    def download_file(self, remote_file_path, local_file_path):
        try:
            file_client = self.get_file_client(remote_file_path)
            download = file_client.download_file()
            downloaded_bytes = download.readall()
            with open(local_file_path, 'wb') as local_file:
                local_file.write(downloaded_bytes)
            
        except Exception as e:
            raise e

    def ls(self, remote_dir):
        try:
            paths = self.file_system_client.get_paths(
                path=remote_dir
            )
            for path in paths:
                print(path.name)
        except Exception as e:
            raise e

    def folder_exists(self, remote_file_path):
        path = "/".join(remote_file_path.split("/")[:-1])
        try:
            dir_client = self.file_system_client.get_directory_client(
                path
            )
            return dir_client.exists()
        except Exception as e:
            raise e

    def makedirs(self, remote_file_path):
        num_nested_folders = len(remote_file_path.split("/")[:-1])
        for index in range(num_nested_folders):
            if not self.folder_exists(remote_file_path, index):
                path = "/".join(remote_file_path.split("/")[:index+1])
                self.create_directory(path)
        
    def copy_file(self, local_file_path, remote_file_path):
        folder_path = "/".join(remote_file_path.split("/")[:-1])
        if not self.folder_exists(folder_path):
            self.makedirs(folder_path)
        self.upload_file(
            local_file_path, remote_file_path
        )
        
    # run before orchestrator
    def recursive_copy(self, root, run_type, version_id, repo_name):
        """
        options for run_type: testing, production, staging
        """
        files_to_copy = []
        for rel_root, directory, files in os.walk(root):
            for File in files:
                files_to_copy.append(
                    os.path.join(rel_root, File)
                )
        for file_path in files_to_copy:
            self.copy_file(
                file_path,
                f"{repo_name}/{run_type}/{version_id}/{file_path}"
            )

def generate_meta_data(
        version_id, run_type, job_id,
        run_id, repo_name, commit_hash
):
    local_file = f"metadata_{version_id}.txt"
    with open(local_file, "w") as f:
        f.write(f"""
        Metadata:
        * job id {job_id}
        * run id {run_id}
        * repo name {repo_name}
        * commit hash {commit_hash}
        * run type {run_type}
        """)
    return local_file

    
def copy_to_blob_storage(connection_string, file_name, container_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob="dags/"+file_name)

    with open(file_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)



    

