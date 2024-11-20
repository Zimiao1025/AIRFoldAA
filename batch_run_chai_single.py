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

        pipeline_url = f"http://10.0.0.12:5000/chai"

        try:
            logger.info(f"------- Requests of pipeline task: {request_dict}")
            requests.post(pipeline_url , json={'request': request_dict})
        except Exception as e:
            logger.error(str(e))


def main():

    with open("./config/temp_chai.json", 'r') as jf:
        request_dict = json.load(jf)
    
    target_dir = "/data/protein/BC_Data/Data/moad_sequence_all/"
    # target_dir = "/data/protein/AIRFold/chai-1/moad_test/"
    output_dir = "/data/protein/BC_Data/Data/moad_apo/"

    prefix = "moad"

    target_files = os.listdir(target_dir)
    for target_file in target_files:
        target_name = target_file.split('.')[0]
        request_dict["name"] = prefix + "_" + target_name

        target_path = target_dir + target_file
        request_dict["fasta_path"] = target_path

        output_path = output_dir + target_name
        mkdir_if_not_exist(output_path)
        request_dict["output_dir"] = output_path

        logger.info(f"------- Received request: {request_dict}")

        call_pipeline(request_dict=request_dict)


if __name__ == "__main__":
    logger.info("------- Start to RUN -------")
    main()
    