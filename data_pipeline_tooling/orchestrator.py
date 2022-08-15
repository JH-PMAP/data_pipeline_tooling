from typing import List, Dict
import requests

def create_job(
        name: str,
        tasks: List[Dict],
        job_clusters: list,
        email_notifications: dict,
        timeout_seconds: int,
        schedule: dict,
        max_concurrent_runs: int,
        job_format: str,
        access_control_list: List[Dict],
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsCreate

    Create a new job.  This is the main work horse of the library.

    Parameters
    ----------
    * name : str - An optional name for the job.
      
    Default: "Untitled"
    
    * tags : dict - A map of tags associated with the job.
    These are forwarded to the cluster as cluster tags for
    jobs clusters, and are subject to the same limitations as
    cluster tags.  A maximum of 25 tags can be added to the job.
    
    Default: empty dict = {}

    * tasks : list of dicts - a list of task
    specfications to be executed by this job.
    
    Default: list with empty dict = [{}]
    
    Note: You can specify a max of 100 items.

    Example task:

    {
    "task_key": "Sessionize",
    "description": "Extracts session data from events",
    "depends_on": [ ],
    "existing_cluster_id": "0923-164208-meows279",
    "spark_jar_task": {
    "main_class_name": "com.databricks.Sessionize",
    
    "parameters": [
      "--data", "dbfs:/path/to/data.json"
    ]

    },
     "libraries": [
      {
       "jar": "dbfs:/mnt/databricks/Sessionize.jar"
      }
     ],
       "timeout_seconds": 86400,
       "max_retries": 3,
       "min_retry_interval_millis": 2000,
       "retry_on_timeout": false
     },

    * job_clusters : list of dicts - A list of job
    cluster specifications that can be shared and
    reused by tasks of this job. Libraries cannot be
    declared in a shared job cluster.  You must declare
    dependent libraries in task settings.

    Default: list with empty dict = [{}]

    Note You can specify a max of 100 items.

    * email_notifications : dict - 
    
    Keys:
      * on_start - who to email on start of job
      * on_success - who to email on success of job
      * on_failure - who to email on failure of job
      * no_alert_for_skipped_runs - boolean

    * timeout_seconds : int - An optional timeout
    applied to each run of this job.  The default 
    behavior is to have no timeout.
    
    * schedule : dict
    
    Keys:
    "quartz_cron_expression": follows cron expression,
    like found here:
    https://www.freeformatter.com/cron-expression-generator-quartz.html
    
    "timezone_id": follows java time zones like found here:
    
    https://docs.trifacta.com/display/DP/Supported+Time+Zone+Values

    "pause_status": "PAUSED" or "UNPAUSED"

    max_concurrent_runs : int - An optional maximum allowed number
    of concurrent runs of the job.
    
    Set this value if you want to be able to execute multiple runs of
    the same job concurrently.  This is useful for example if you
    trigger your job on a frequent schedule and want to allow consecutive 
    runs to overlap with each other, or if you want to trigger multiple
    runs which differ by their input parameters.
    
    This setting affects only new runs.  For example, suppose the
    job's concurrency is 4 and there are 4 concurrent active runs.
    Then setting the concurrency to 3 won't kill any of the active runs.
    However, from then on, new runs are skipped unless there are fewer than
    3 active runs.

    This value cannot exceed 1000.  Setting this value to 0 causes all new
    runs to be skipped.  
    
    Default: 1.

    * job_format : str - Used to tell what the format of the job is.
    This field is ignored in Create/Update/Reset calls.
    
    Values: "SINGLE_TASK" or "MULTI_TASK"

    Default: "MULTI_TASK"

    * access_control_list : list of dicts - 
    
    Whoever creates the job should always set
    {
     "user_name": [YOUR EMAIL GOES HERE],
     "permission_level": "IS_OWNER"
    }
    
    You can also set secondary users to "permission_level": "CAN_MANAGE"
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    parameters = {
        "name": name,
        "tasks": tasks,
        "job_clusters": job_clusters,
        "email_notifications": email_notifications,
        "timeout_seconds": str(timeout_seconds),
        "schedule": schedule,
        "max_concurrent_runs": max_concurrent_runs,
        "format": job_format,
        "access_control_list": access_control_list,
    }
        
    response = requests.post(
        f'{host}/api/2.1/jobs/create',
        headers=headers,
        json=parameters
    )
    return response

def get_jobs(
        limit: int,
        offset: int,
        expand_tasks: bool,
        host: str,
        api: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsList

    Retrieves a list of jobs.
    
    Parameters
    ----------
    
    * limit : int - The number of jobs to return.  
    0 < limit <= 25.  Default is 20. 
    
    * offset : int - The offset of the first job
    to return, relative to the most recently created
    job.  

    Example:

    Offset = 0, returns the most recently created job.
    
    * expand_tasks : bool -
    Whether to include task and cluster details in the
    response.

    * host : str - the host IP Address
    
    * api : str - the api version to use.  
    
    Note: 2.1 is suggested

    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    parameters = {
        "limit": str(limit),
        "offset": str(offset),
        "expand_tasks": str(expand_tasks).lower()
    }
    response = requests.get(
        f'{host}{api}/jobs/list',
        headers=headers,
        json=parameters
    )
    return response

def get_job(job_id: int, host: str, headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsGet

    Retrieves the details for a single job.

    Parameters
    ----------

    * job_id : int - The canonical identifier of the job to
    retrieve information about.
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    parameters = {
        "job_id": str(job_id)
    }
    
    response = requests.get(
        f'{host}/api/2.1/jobs/get',
        headers=headers,
        json=parameters
    )
    return response

def update_job_settings(
        job_id: int,
        new_settings: dict,
        host: str,
        headers: dict
        ) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsUpdate

    Add, update, or remove specific settings of an existing job. 
    Use the Reset endpoint to overwrite all job settings.

    Parameters
    ----------

    * job_id : int - The canonical identifier of the job to
    retrieve information about.
    
    * new_settings: dict - A list of new settings.  

    Settings that can be updated:
        * name
        * tasks
        * job_clusters
        * email_notifications
        * timeout_seconds
        * schedule
        * max_concurrent_runs
        * job_format
        * access_control_list

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    job_parameters = get_job(job_id, host, api)
    for key in job_parameters:
        if key in new_settings:
            job_parameters[key] = new_settings[key]

    parameters = {
        "job_id": str(job_id),
        "new_settings": job_parameters
    }   
    response = requests.post(
        f'{host}/api/2.1/jobs/update',
        headers=headers,
        json=parameters
    )
    return response

def reset_job_settings(
        job_id: int,
        name: str,
        tasks: List[Dict],
        job_clusters: list,
        email_notifications: dict,
        timeout_seconds: int,
        schedule: dict,
        max_concurrent_runs: int,
        job_format: str,
        access_control_list: List[Dict],
        host: str,
        headers: dict
        ) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsReset

    Overwrites all the settings for a specific job. Use the Update endpoint to update job settings partially.

    Parameters
    ----------

    * job_id : int - The canonical identifier of the job to
    retrieve information about.


    * name : str - An optional name for the job.
      
    Default: "Untitled"
    
    * tags : dict - A map of tags associated with the job.
    These are forwarded to the cluster as cluster tags for
    jobs clusters, and are subject to the same limitations as
    cluster tags.  A maximum of 25 tags can be added to the job.
    
    Default: empty dict = {}

    * tasks : list of dicts - a list of task
    specfications to be executed by this job.
    
    Default: list with empty dict = [{}]
    
    Note: You can specify a max of 100 items.

    Example task:

    {
    "task_key": "Sessionize",
    "description": "Extracts session data from events",
    "depends_on": [ ],
    "existing_cluster_id": "0923-164208-meows279",
    "spark_jar_task": {
    "main_class_name": "com.databricks.Sessionize",
    
    "parameters": [
      "--data", "dbfs:/path/to/data.json"
    ]

    },
     "libraries": [
      {
       "jar": "dbfs:/mnt/databricks/Sessionize.jar"
      }
     ],
       "timeout_seconds": 86400,
       "max_retries": 3,
       "min_retry_interval_millis": 2000,
       "retry_on_timeout": false
     },

    * job_clusters : list of dicts - A list of job
    cluster specifications that can be shared and
    reused by tasks of this job. Libraries cannot be
    declared in a shared job cluster.  You must declare
    dependent libraries in task settings.

    Default: list with empty dict = [{}]

    Note You can specify a max of 100 items.

    * email_notifications : dict - 
    
    Keys:
      * on_start - who to email on start of job
      * on_success - who to email on success of job
      * on_failure - who to email on failure of job
      * no_alert_for_skipped_runs - boolean

    * timeout_seconds : int - An optional timeout
    applied to each run of this job.  The default 
    behavior is to have no timeout.
    
    * schedule : dict
    
    Keys:
    "quartz_cron_expression": follows cron expression,
    like found here:
    https://www.freeformatter.com/cron-expression-generator-quartz.html
    
    "timezone_id": follows java time zones like found here:
    
    https://docs.trifacta.com/display/DP/Supported+Time+Zone+Values

    "pause_status": "PAUSED" or "UNPAUSED"

    max_concurrent_runs : int - An optional maximum allowed number
    of concurrent runs of the job.
    
    Set this value if you want to be able to execute multiple runs of
    the same job concurrently.  This is useful for example if you
    trigger your job on a frequent schedule and want to allow consecutive 
    runs to overlap with each other, or if you want to trigger multiple
    runs which differ by their input parameters.
    
    This setting affects only new runs.  For example, suppose the
    job's concurrency is 4 and there are 4 concurrent active runs.
    Then setting the concurrency to 3 won't kill any of the active runs.
    However, from then on, new runs are skipped unless there are fewer than
    3 active runs.

    This value cannot exceed 1000.  Setting this value to 0 causes all new
    runs to be skipped.  
    
    Default: 1.

    * job_format : str - Used to tell what the format of the job is.
    This field is ignored in Create/Update/Reset calls.
    
    Values: "SINGLE_TASK" or "MULTI_TASK"

    Default: "MULTI_TASK"

    * access_control_list : list of dicts - 
    
    Whoever creates the job should always set
    {
     "user_name": [YOUR EMAIL GOES HERE],
     "permission_level": "IS_OWNER"
    }
    
    You can also set secondary users to "permission_level": "CAN_MANAGE"
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """

    parameters = {
        "job_id": str(job_id),
        "new_settings": {
            "name": name,
            "tasks": tasks,
            "job_clusters": job_clusters,
            "email_notifications": email_notifications,
            "timeout_seconds": str(timeout_seconds),
            "schedule": schedule,
            "max_concurrent_runs": max_concurrent_runs,
            "format": job_format,
            "access_control_list": access_control_list
        }
    }
            
    response = requests.post(
        f'{host}/api/2.1/jobs/update',
        headers=headers,
        json=parameters
    )
    return response

def delete_job(job_id: int, host: str, headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsDelete

    Parameters
    ----------

    * job_id : int - The canonical identifier of the job to
    retrieve information about.
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    
    """
    parameters = {
        "job_id": str(job_id)
    }

    response = requests.post(
        f'{host}/api/2.1/jobs/delete',
        headers=headers,
        json=parameters
    )
    return response

def execute_job(
        job_id: int,
        host: str,
        headers: dict,
        idempotency_token : str = None,
        jar_params: List = None,
        notebook_params: List[Dict] = None,
        python_params: List = None,
        spark_submit_params: List = None,
        pipeline_params : dict = {"full_refresh": False}
        ) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunNow

    Run a job and return the run_id of the triggered run.

    Parameters
    ----------

    * job_id : int - The canonical identifier of the job to
    retrieve information about.

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  

    * pipeline_params : dict - 
    
    A dictionary with one key-value pair:
    
       full_refresh : bool - If true, triggers a full refresh on the delta live table.

    * idempotency_token : str - [Optional]
    
    An optional token to guarantee the idempotency of job run requests. 
    If a run with the provided token already exists, 
    the request does not create a new run but returns the 
    ID of the existing run instead. 
    If a run with the provided token is deleted, an error is returned.

    If you specify the idempotency token, 
    upon failure you can retry until the request succeeds. 
    Databricks guarantees that exactly one run is launched with that idempotency token.

    This token must have at most 64 characters.
    

    The following parameters are optional, but at most
    one of the following can be passed:
    
    * jar_params : list - A list of parameters for jobs with Spark JAR tasks, 
    for example "jar_params": ["john doe", "35"]. The parameters are used to invoke 
    the main function of the main class specified in the Spark JAR task. 
    If not specified upon run-now, it defaults to an empty list. 
    jar_params cannot be specified in conjunction with notebook_params. 
    The JSON representation of this field 
    (for example {"jar_params":["john doe","35"]}) cannot exceed 10,000 bytes.

    * notebook_params : list[dict] - 
    A map from keys to values for jobs with notebook task, 
    for example "notebook_params": {"name": "john doe", "age": "35"}. 
    The map is passed to the notebook and is 
    accessible through the dbutils.widgets.get function.
    If not specified upon run-now, the triggered run uses the job’s base parameters.
    notebook_params cannot be specified in conjunction with jar_params.
    Use Task parameter variables to set parameters containing information about job runs.
    The JSON representation of this field (for example {"notebook_params":{"name":"john doe","age":"35"}}) 
    cannot exceed 10,000 bytes.

    * python_params : list - 

    A list of parameters for jobs with Python tasks, 
    for example "python_params": ["john doe", "35"]. 
    The parameters are passed to Python file as command-line parameters. 
    If specified upon run-now, it would overwrite the parameters specified in job setting. 
    The JSON representation of this field 
    (for example {"python_params":["john doe","35"]}) cannot exceed 10,000 bytes.

    Use Task parameter variables to set parameters containing information about job runs.

    Important

    These parameters accept only Latin characters (ASCII character set). 
    Using non-ASCII characters returns an error. 
    Examples of invalid, non-ASCII characters are Chinese, Japanese kanjis, and emojis.

    * spark_submit_params : list - 
    A list of parameters for jobs with spark submit task, 
    for example "spark_submit_params": 
    ["--class", "org.apache.spark.examples.SparkPi"]. 
    The parameters are passed to spark-submit script as command-line parameters. 
    If specified upon run-now, it would overwrite the parameters specified in job setting. 
    The JSON representation of this field 
    (for example {"python_params":["john doe","35"]}) cannot exceed 10,000 bytes.

    Use Task parameter variables to set parameters containing information about job runs.

    Important

    These parameters accept only Latin characters (ASCII character set). 
    Using non-ASCII characters returns an error. Examples of invalid, 
    non-ASCII characters are Chinese, Japanese kanjis, and emojis.
    """
    parameters = {
        "job_id": str(job_id),
    }
    if idempotency_token:
        parameters["idempotency_token"] = idempotency_token
    if jar_params:
        parameters["jar_params"] = jar_parms
    if notebook_params:
        parameters["notebook_params"] = notebook_params
    if python_params:
        parameters["python_params"] = python_params
    if spark_submit_params:
        parameters["spark_submit_params"] = spark_submit_params

    response = requests.post(
        f'{host}/api/2.1/jobs/run-now',
        headers=headers,
        json=parameters
    )
    return response

def execute_standalone_job(
        tasks: List[Dict],
        job_clusters: List[Dict],
        run_name: str,
        timeout_seconds: int,
        idempotency_token: str,
        access_control_list: List[Dict],
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsSubmit

    Submit a one-time run. 
    This endpoint allows you to submit a workload directly without creating a job. 
    Runs submitted using this endpoint don’t display in the UI. 
    Use the jobs/runs/get API to check the run state after the job is submitted.
    
    Parameters
    ----------
    * tasks : list of dicts - a list of task
    specfications to be executed by this job.
    
    Default: list with empty dict = [{}]
    
    Note: You can specify a max of 100 items.

    Example task:

    {
    "task_key": "Sessionize",
    "description": "Extracts session data from events",
    "depends_on": [ ],
    "existing_cluster_id": "0923-164208-meows279",
    "spark_jar_task": {
    "main_class_name": "com.databricks.Sessionize",
    
    "parameters": [
      "--data", "dbfs:/path/to/data.json"
    ]

    },
     "libraries": [
      {
       "jar": "dbfs:/mnt/databricks/Sessionize.jar"
      }
     ],
       "timeout_seconds": 86400,
       "max_retries": 3,
       "min_retry_interval_millis": 2000,
       "retry_on_timeout": false
     },

    * job_clusters : list of dicts - A list of job
    cluster specifications that can be shared and
    reused by tasks of this job. Libraries cannot be
    declared in a shared job cluster.  You must declare
    dependent libraries in task settings.

    Default: list with empty dict = [{}]

    Note You can specify a max of 100 items.

    * email_notifications : dict - 
    
    Keys:
      * on_start - who to email on start of job
      * on_success - who to email on success of job
      * on_failure - who to email on failure of job
      * no_alert_for_skipped_runs - boolean

    * run_name : str - 
    
    An optional name for the run. The default value is Untitled

    * timeout_seconds : int - An optional timeout
    applied to each run of this job.  The default 
    behavior is to have no timeout.

    * idempotency_token : str - [Optional]
    
    An optional token to guarantee the idempotency of job run requests. 
    If a run with the provided token already exists, 
    the request does not create a new run but returns the 
    ID of the existing run instead. 
    If a run with the provided token is deleted, an error is returned.

    If you specify the idempotency token, 
    upon failure you can retry until the request succeeds. 
    Databricks guarantees that exactly one run is launched with that idempotency token.

    This token must have at most 64 characters.

    * access_control_list : list of dicts - 
    
    Whoever creates the job should always set
    {
     "user_name": [YOUR EMAIL GOES HERE],
     "permission_level": "IS_OWNER"
    }
    
    You can also set secondary users to "permission_level": "CAN_MANAGE"

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    parameters = {
        "tasks": tasks,
        "job_clusters": job_clusters,
        "run_name": run_name,
        "timeout_seconds": str(timeout_seconds),
        "idempotency_token": idempotency_token,
        "access_control_list": access_control_list,
    }
    
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/submit',
        headers=headers,
        json=parameters
    )
    return response

def get_runs_for_job(
        active_only : bool,
        completed_only: bool,
        offset : int,
        limit: int,
        job_id: int,
        run_type: str,
        expand_tasks: bool,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsList

    List runs in descending order by start time.

    Parameters
    -----------
    
    * active_only : bool - 
    If active_only is true only active runs are included.

    * completed_only : bool - 
    If completed_only is true, only completed runs 
    are included in the results.

    * offset : int - The offset of the first job
    to return, relative to the most recently created
    job.  

    * limit : int - The number of jobs to return.  
    0 < limit <= 25.  Default is 20. 
        
    * job_id : int - The canonical identifier of the job to
    retrieve information about.

    * run_type : str - 
    
    The type of runs to return. For a description of run types.
    Options:
    * JOB_RUN
    * WORKFLOW_RUN
    * SUBMIT_RUN
    
    * expand_tasks : bool - 
    Whether to include task and cluster details in the response.

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    parameters = {
        "job_id": str(job_id),
        "active_only": str(active_only).lower(),
        "completed_only": str(completed_only).lower(),
        "offset": str(offset),
        "lmit": str(limit),
        "run_type": run_type,
        "expand_tasks": str(expand_tasks).lower(),
    }
    
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/list',
        headers=headers,
        json=parameters
    )

    return response

def get_runs_for_joblist(
        active_only: bool,
        completed_only: bool,
        offset: int,
        limit: int,
        run_type: str,
        expand_tasks: bool,
        start_time_from : int,
        start_time_to : int,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsList

    List runs in descending order by start time.

    Parameters
    ----------
    
    * active_only : bool - 
    If active_only is true only active runs are included.

    * completed_only : bool - 
    If completed_only is true, only completed runs 
    are included in the results.
    
    * expand_tasks : bool -
    Whether to include task and cluster details in the
    response.

    * limit : int - The number of jobs to return.  
    0 < limit <= 25.  Default is 20. 
    
    * run_type : str - 
    
    The type of runs to return. For a description of run types.
    Options:
    * JOB_RUN
    * WORKFLOW_RUN
    * SUBMIT_RUN

    * offset : int - The offset of the first job
    to return, relative to the most recently created
    job.  

    * start_time_from : int - show runs that started at or after
    this value.  The value must be a UTC timestamp in milliseconds.
    
    * start_time_to : int - show runs that started at or before 
    this value.  The value must be a UTC timestamp in milliseconds.

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  

    """
    parameters = {
        "active_only": str(active_only).lower(),
        "completed_only": str(completed_only).lower(),
        "offset": str(offset),
        "lmit": str(limit),
        "run_type": run_type,
        "expand_tasks": str(expand_tasks).lower(),
        "start_time_from": start_time_from,
        "start_time_to": start_time_to
    }
    
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/list',
        headers=headers,
        json=parameters
    )
    return response

def get_run(
        run_id: int,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsGet

    Retrieve the metadata for a run.
    
    Parameters
    -----------
    * run_id : int - 
    The canonical identifier of the run for which to
    retrieve the metadata. 

    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    """
    
    parameters = {
        "run_id": str(run_id)
    }
    
    response = requests.get(
        f'{host}/api/2.1/jobs/runs/get',
        headers=headers,
        json=parameters
    )
    return response

def copy_code_to_notebook(
        run_id: int,
        host: str,
        headers: dict,
        views_to_export: str = "CODE") -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsExport
    
    Export and retrieve the job run task.

    Parameters
    ----------

    * run_id : int - 
    The canonical identifier of the run for which to
    retrieve the metadata. 

    * views_to_export : str - 

    An enumerable with values:
    * CODE
    * DASHBOARDS
    * ALL
    
    Default is CODE.
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  

    """
    parameters = {
        "run_id": str(run_id),
        "views_to_export": views_to_export
    }
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/export',
        headers=headers,
        json=parameters
    )
    return response

def cancel_run(
        run_id: str,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsCancel

    Cancels a job run. The run is canceled asynchronously, 
    so it may still be running when this request completes.
    
    Parameters
    ----------
    * run_id : int - 
    The canonical identifier of the run for which to
    retrieve the metadata. 
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  

    """
    parameters = {
        "run_id": str(run_id)
    }
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/cancel',
        headers=headers,
        json=parameters
    )
    return response

def get_output(
        run_id: str,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsGetOutput

    Retrieve the output and metadata of a run. 
    When a notebook task returns a value through the dbutils.notebook.exit() call, 
    you can use this endpoint to retrieve that value. 
    Databricks restricts this API to return the first 5 MB of the output. 
    To return a larger result, you can store job results in a cloud storage service. 
    This endpoint validates that the run_id parameter is valid and returns an HTTP 
    status code 400 if the run_id parameter is invalid. Runs are automatically 
    removed after 60 days. If you to want to reference them beyond 60 days, 
    you must save old run results before they expire. 
    To export using the UI, see Export job run results. 
    To export using the Jobs API, see Runs export.

    Parameters
    ----------
    * run_id : int - 
    The canonical identifier of the run for which to
    retrieve the metadata. 
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  

    """
    parameters = {
        "run_id": str(run_id)
    }
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/get-output',
        headers=headers,
        json=parameters
    )
    return response

def delete_run(
        run_id: str,
        host: str,
        headers: dict) -> requests.Response:
    """
    Original Docs: https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsDelete

    Deletes a non-active run. Returns an error if the run is active.

    Parameters
    ----------
    * run_id : int - 
    The canonical identifier of the run for which to
    retrieve the metadata. 
    
    * host : str - the host IP Address
    
    * headers: dict - the headers come from the config 
    and should not be changed  
    
    """
    parameters = {
        "run_id": str(run_id)
    }
    response = requests.post(
        f'{host}/api/2.1/jobs/runs/delete',
        headers=headers,
        json=parameters
    )
    return response

