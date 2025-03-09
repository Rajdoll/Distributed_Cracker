import redis
import os
import subprocess
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

UPLOAD_FOLDER = '/data'
r = redis.Redis(host='cracker-service', port=6379, db=0)
#docker compose: r = redis.Redis(host='redis', port=6379, db=0)

def process_task(task_id, part_number):
    logging.info(f"Memulai proses task {task_id} part {part_number}")
    
    try:
        hash_file = f"{UPLOAD_FOLDER}/{task_id}_hash.txt"
        wordlist_part = f"{UPLOAD_FOLDER}/{task_id}_part{part_number}.txt"
        result_file = f"{UPLOAD_FOLDER}/{task_id}_result{part_number}.txt"

        logging.info(f"Hash file: {hash_file}")
        logging.info(f"Wordlist part: {wordlist_part}")

        if not os.path.exists(hash_file):
            logging.error(f"Hash file {hash_file} not found")
            return
        if not os.path.exists(wordlist_part):
            logging.error(f"Wordlist part {wordlist_part} not found")
            return

        with open(hash_file, 'r') as f:
            logging.info(f"Hash file content: {f.read().strip()}")
        with open(wordlist_part, 'r') as f:
            logging.info(f"Wordlist part content: {f.read().strip()}")

        command = f"hashcat -m 0 -a 0 {hash_file} {wordlist_part} --force --potfile-disable -o {result_file} --outfile-format=2"
        logging.info(f"Running command: {command}")
        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        logging.info(f"Hashcat Output: {stdout}")
        if stderr:
            logging.error(f"Hashcat Error: {stderr}")
        logging.info(f"Hashcat return code: {process.returncode}")
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                logging.info(f"Result file content: {f.read().strip()}")
        else:
            logging.error(f"Result file {result_file} not created")

        if process.returncode in (0, 1):
            current_progress = int(r.get(task_id) or 0)
            new_progress = min(current_progress + 25, 100)
            if part_number == "3":
                r.set(task_id, 100)
            else:
                r.set(task_id, new_progress)
            logging.info(f"Task {task_id} part {part_number} completed with return code {process.returncode}, progress set to {new_progress}")
        else:
            logging.error(f"Hashcat failed with return code {process.returncode}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == '__main__':
    logging.info("Worker started")
    while True:
        task_data = r.blpop('tasks')
        if task_data:
            task_id, part_number = task_data[1].decode().split(':')
            process_task(task_id, part_number)