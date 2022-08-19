from .artifact_store import AzureDataLakeClient
from . import orchestrator
import os
import sys


class Orca:
    def __init__(self):
        pass
    
    def create_job(
            self,
            job_name : str,
            file_name : str,
            file_path : str,
            run_type : str,
            version_id : int,
            max_concurrent_runs : int,
            timeout_seconds : int,
            schedule : str,
            config : bool = True,
            cluster_id : str = None,
            storage_account_name : str = None,
            storage_account_key : str = None,
            host : str= None,
            headers : dict = None,
            filesystem_name : str = None,
            user_name : str = None,
            email_notifications : dict = None,
            repo_name : str = None,
            project : str = None,
            write_out_to_config : bool = False,
            timezone_id : str = "America/New_York",
            pause_status : str = "PAUSED",
    ):
        """

        This function is the main work horse for the entire tool.
        You can use it to create jobs on databricks, which can then be scheduled and run
        through airflow or any other orchestration engine.
        
        Notes:
        Use https://www.freeformatter.com/cron-expression-generator-quartz.html 
        for the schedule formatting.

        Use https://garygregory.wordpress.com/2013/06/18/what-are-the-java-timezone-ids/
        for the timezone id.

        Parameters
        ----------
        * job_name : str - the name of the job
        
        * file_name : str - the name of the file to upload
        
        * file_path : str - the path without the file_name. 

        Default : ./ 

        Note: The author typically only will upload from 
        the current working directory unless I'm traversing 
        a set of files and want that structure maintained
        on the databricks mount.
        
        * run_type : str - this is an enumeration, technically.
        You can set it to be whatever you want, but the convention
        the author likes is:
        * test
        * debug
        * production
        
        * version_id : int - the version of the code to upload,
        helpful for testing and debugging.
        
        * max_concurrent_runs : int - the maximum concurrent runs
        that can be performed.
        
        * timeout_seconds : int - the number of seconds to allow
        before timing out if the job isn't doing any work actively.
        The author typically sets this to 30, but use your own best 
        judgement.
        
        Default : 30
        
        * schedule : str - this is the schedule the job should run on
        so like every minute, every day, every day at noon.  The
        syntax for the scheduler is confusing, but this formatter
        helps:
        
        https://www.freeformatter.com/cron-expression-generator-quartz.html 
        
        * config [optional] : bool - whether to read from a config file, named
        config.py or not.
        Note: must be in the same directory as the tool is being run from.
        
        The following fields are optional only if they exist in the config.
        Otherwise they are required:
        
        * cluster_id [optional] : str - an existing cluster id to run the job on.
        
        * storage_account_name [optional] : str - an azure datalake storage account name.

        * storage_account_key [optional] : str - an azure datalake storage account key.
        
        Note: the storage account MUST be mounted in databricks using the mount function below,
        or the jobs will not be available in databricks.  The mount function is called:
        `databricks_mount_container_blob`
        
        * host [optional] : str - the host IP Address
    
        * headers [optional] : dict - the headers come from the config 
        and should not be changed  

        * filesystem_name [optional] : str - the name of the azure datalake filesystem.
        
        * user_name [optional] : str - the email address associated with a databricks account.
        
        * email_notifications [optional] : bool - whether to notify the user by email on
        job failures.

        * repo_name [optional] : str - the name of the github repo 
        (or other version control system repo name).

        * project [optional] : str - the name of the project.
        
        END of 'semi optional' parameters
        
        * write_out_to_config [optional] : bool - if the parameters 
        were passed in to the function, if set to True, then they will
        be written out to a file called config.py
        
        * timezone_id [optional] : str - this is optional in the sense
        that a default parameter value is passed.  It is _required_.
        
        Default: "America/New_York"
        
        For more options see: 

        https://garygregory.wordpress.com/2013/06/18/what-are-the-java-timezone-ids/

        * pause_status : str - possible values:
        
        * "PAUSED"
        * "UNPAUSED"

        If job is paused, then it doesn't run even when executed.  To 'actually' run
        it must be in the UNPAUSED state.
        
        """
        self.max_concurrent_runs = max_concurrent_runs
        self.job_name = job_name
        self.file_name = file_name
        self.file_path = file_path
        self.run_type = run_type
        self.version_id = version_id
        self.cluster_id = cluster_id
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.host = host
        self.headers = headers
        self.filesystem_name = filesystem_name
        self.user_name = user_name
        self.email_notifications = email_notifications
        self.timeout_seconds = timeout_seconds
        self.repo_name = repo_name
        self.project = project
        if config:
            self.read_config()

        task_file_path = self.upload_task(
            self.file_name,
            storage_account_name=self.storage_account_name,
            storage_account_key=self.storage_account_key,
            run_type=self.run_type,
            version_id=self.version_id,
            repo_name=self.repo_name,
            file_path=self.file_path,
            filesystem_name=self.filesystem_name,
            project=self.project,
            config=False
        )

        job_format = "SINGLE_TASK"
        tasks = [
        {
            "task_key": self.job_name,
            "description": "",
            "depends_on": [],
            "existing_cluster_id": self.cluster_id,
            "spark_python_task": {
                "python_file": task_file_path,
                "parameters": []
            },
            "timeout_seconds": 1000,
            "max_retries": 3,
            "min_retry_interval_millis": 10000,
            "retry_on_timeout": "true",
        }]
        job_clusters = []
        schedule = {
            "quartz_cron_expression": f"{schedule}",
            "timezone_id": timezone_id,
            "pause_status": pause_status
        }
        max_concurrent_runs = self.max_concurrent_runs

        access_control_list = [
            {"user_name": self.user_name,
             "permission_level": "IS_OWNER"}
        ]
        job = orchestrator.create_job(
            self.job_name,
            tasks,
            job_clusters,
            self.email_notifications,
            timeout_seconds,
            schedule,
            self.max_concurrent_runs,
            job_format,
            access_control_list,
            self.host,
            self.headers
        )
        
        print(f"Task File Path: {task_file_path}")
        print(f"Job ID: {int(job.json()['job_id'])}")

        if write_out_to_config:

            job_identifier = file_name.split(".")[0]
            with open(f"airflow_config_{self.repo_name}_{self.run_type}_{self.version_id}.py", "a") as f:
                f.write(f"job_{job_identifier} = {int(job.json()['job_id'])}\n")
                f.write(f"task_{job_identifier} = '{task_file_path}'\n")
                # add file name to write out
    
    def upload_task(
            self,
            file_name : str,
            run_type : str,
            storage_account_name : str = None,
            storage_account_key : str = None,
            version_id : int = None,
            repo_name : str = None,
            file_path : str = None,
            filesystem_name : str = None,
            project : str = None,
            config : bool = True,
    ):
        """
        Uploads a task to azure datalake.
        
        Parameters
        -----------
        
        * file_name : str - the name of the file to upload
                
        * file_path : str - the path without the file_name. 

        Default : ./ 

        Note: The author typically only will upload from 
        the current working directory unless I'm traversing 
        a set of files and want that structure maintained
        on the databricks mount.

        * run_type : str - this is an enumeration, technically.
        You can set it to be whatever you want, but the convention
        the author likes is:
        * test
        * debug
        * production
        
        * version_id : int - the version of the code to upload,
        helpful for testing and debugging.
        
        * storage_account_name [optional] : str - an azure datalake storage account name.

        * storage_account_key [optional] : str - an azure datalake storage account key.
        
        Note: the storage account MUST be mounted in databricks using the mount function below,
        or the jobs will not be available in databricks.  The mount function is called:
        `databricks_mount_container_blob`
        
        * filesystem_name [optional] : str - the name of the azure datalake filesystem.
        
        * repo_name [optional] : str - the name of the github repo 
        (or other version control system repo name).

        * project [optional] : str - the name of the project.

        * config [optional] : bool - if True read from the config.py
        Don't read if False.
        """
        if config:
            self.read_config()

        storage_account_name = self.storage_account_name
        storage_account_key = self.storage_account_key
        repo_name = self.repo_name
        filesystem_name = self.filesystem_name
        project = self.project

        datalake_client = AzureDataLakeClient(
            storage_account_name,
            filesystem_name,
            storage_account_key=storage_account_key
        )
        if file_path == './':
            directory = f"{repo_name}/{run_type}/{version_id}/"
        else:
            directory = f"{repo_name}/{run_type}/{version_id}/{file_path}"
        datalake_client.create_directory(directory)
        datalake_client.upload_file(file_path+file_name, directory+file_name)
        return f"dbfs:/mnt/{project}/{directory}{file_name}"

    def execute_job(self, job_id):
        """
        Executes a give job.
        
        Parameters
        ----------
        
        * job_id : int - the job id to execute
        on databricks.
        """
        orchestrator.execute_job(
            job_id, 
            host,
            headers,
            jar_params,
            notebook_params,
            python_params,
            spark_submit_params
        )
        
    def read_config(self):
        """
        Reads a config.py in the current directory.
        """
        sys.path.append(os.getcwd())
        from config import (
            headers, host,
            storage_account_name,
            storage_account_key,
            cluster_id, filesystem_name,
            user_name, email_notifications,
            repo_name, project
        )
        self.headers = headers
        self.host = host
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.cluster_id = cluster_id
        self.filesystem_name = filesystem_name
        self.user_name = user_name
        self.email_notifications = email_notifications
        self.repo_name = repo_name
        self.project = project

def create_jobs_and_upload(
        file_names, job_names, run_type, version_id,
        max_concurrent_runs, timeout_seconds, schedule,
        config=True, cluster_id=None, storage_account_name=None,
        storage_account_key=None, host=None, headers=None, filesystem_name=None,
        user_name=None, email_notifications=None, repo_name=None, project=None,
        write_out_to_config=False):
    """
    Creates a set of jobs.
    
    Parameters
    ----------
    * job_names : list - the names of the jobs

    * file_names : list - the names of the files to upload

    * run_type : str - this is an enumeration, technically.
    You can set it to be whatever you want, but the convention
    the author likes is:
    * test
    * debug
    * production

    * version_id : int - the version of the code to upload,
    helpful for testing and debugging.

    * max_concurrent_runs : int - the maximum concurrent runs
    that can be performed.

    * timeout_seconds : int - the number of seconds to allow
    before timing out if the job isn't doing any work actively.
    The author typically sets this to 30, but use your own best 
    judgement.

    Default : 30

    * schedule : str - this is the schedule the job should run on
    so like every minute, every day, every day at noon.  The
    syntax for the scheduler is confusing, but this formatter
    helps:

    https://www.freeformatter.com/cron-expression-generator-quartz.html 

    * config [optional] : bool - whether to read from a config file, named
    config.py or not.
    Note: must be in the same directory as the tool is being run from.

    The following fields are optional only if they exist in the config.
    Otherwise they are required:

    * cluster_id [optional] : str - an existing cluster id to run the job on.

    * storage_account_name [optional] : str - an azure datalake storage account name.

    * storage_account_key [optional] : str - an azure datalake storage account key.

    Note: the storage account MUST be mounted in databricks using the mount function below,
    or the jobs will not be available in databricks.  The mount function is called:
    `databricks_mount_container_blob`

    * host [optional] : str - the host IP Address

    * headers [optional] : dict - the headers come from the config 
    and should not be changed  

    * filesystem_name [optional] : str - the name of the azure datalake filesystem.

    * user_name [optional] : str - the email address associated with a databricks account.

    * email_notifications [optional] : bool - whether to notify the user by email on
    job failures.

    * repo_name [optional] : str - the name of the github repo 
    (or other version control system repo name).

    * project [optional] : str - the name of the project.

    END of 'semi optional' parameters

    * write_out_to_config [optional] : bool - if the parameters 
    were passed in to the function, if set to True, then they will
    be written out to a file called config.py

    * timezone_id [optional] : str - this is optional in the sense
    that a default parameter value is passed.  It is _required_.

    Default: "America/New_York"

    For more options see: 

    https://garygregory.wordpress.com/2013/06/18/what-are-the-java-timezone-ids/

    * pause_status : str - possible values:

    * "PAUSED"
    * "UNPAUSED"

    If job is paused, then it doesn't run even when executed.  To 'actually' run
    it must be in the UNPAUSED state.
        

    """
    
    orca = Orca()
    for index, file_name in enumerate(file_names):
        # we set a convention that the filepath
        # is always the root folder, for now
        # if this becomes unweildy we can change it later
        file_path = "./"
        job_name = job_names[index]
        orca.create_job(
            job_name, file_name, file_path, run_type,
            version_id, max_concurrent_runs, timeout_seconds,
            schedule, config=config, cluster_id=cluster_id,
            storage_account_name=storage_account_name,
            storage_account_key=storage_account_key, host=host,
            headers=headers, filesystem_name=filesystem_name,
            user_name=user_name, email_notifications=email_notifications,
            repo_name=repo_name, project=project,
            write_out_to_config=write_out_to_config,
        )

def databricks_mount_container_blob(
  storage_account_name: str,
  container_name: str,
  secrets_scope: str,
  secrets_key: str
):
  '''
  Mounts a datalake file system to databricks.
  
  Parameters
  ----------
  storage_account_name - name of azure storage account
  container_name - name of container in azure storage account
  secrets_scope - databricks secrets scope name
  secrets_key - databricks secrets key in secrets scope
  '''
  access_key = dbutils.secrets.get(scope=secrets_scope, key=secrets_key)
  conf_key = f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net"
  
  try:
    dbutils.fs.mount(
      source = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net",
      mount_point = f"/mnt/{container_name}",
      extra_configs = {conf_key: access_key})
    
    print(f"{container_name} container from {storage_account_name} storage account has been mounted with mountname {container_name}")
    
  except Exception as e:
    print(f"Error mounting container, check configurations ")
