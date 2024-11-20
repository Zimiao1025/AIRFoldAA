import json
import os
import sys
import requests
from traceback import print_exception
from loguru import logger

from lib.utils import tool_utils


def mkdir_if_not_exist(tmpdir):
    ''' create folder if not exists '''
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)


def call_pipeline(request_dict):
    try:
        logger.info(
            f"start processing {len(request_dict)} requests"
            f"\n{json.dumps(request_dict)}"
        )
        pipelineWorker(request_dict)
                    
    except:
        print_exception(*sys.exc_info())
                

def pipelineWorker(request_dict):
    
    with tool_utils.tmpdir_manager(base_dir="/tmp") as tmpdir:
        os.path.join(tmpdir, "requests.pkl")

        pipeline_url = f"http://10.0.0.12:5000/alphafold3"

        try:
            logger.info(f"------- Requests of pipeline task: {request_dict}")
            requests.post(pipeline_url , json={'request': request_dict})
        except Exception as e:
            logger.error(str(e))


def main():

    with open("./config/temp_af3.json", 'r') as jf:
        request_dict = json.load(jf)
    logger.info(f"------- Received request: {request_dict}")
    call_pipeline(request_dict=request_dict)



    # json_dir = "/data/protein/AIRFold/E3_complex_validation_v0_af3_json/"
    # json_files = os.listdir(json_dir)
    # for json_file in json_files[1:6]:
    #     request_dict["json_path"] = json_dir + json_file

    #     logger.info(f"------- Received request: {request_dict}")

    #     call_pipeline(request_dict=request_dict)


if __name__ == "__main__":
    logger.info("------- Start to RUN -------")
    main()
    