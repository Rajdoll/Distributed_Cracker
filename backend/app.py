from flask import Flask, request, jsonify
import redis
import uuid
import os

app = Flask(__name__)
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379"))
)

try:
    r.ping()
    print("✅ Connected to Redis")
except Exception as e:
    print(f"❌ Redis connection error: {str(e)}")

UPLOAD_FOLDER = '/data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'hash' not in request.files or 'wordlist' not in request.files:
            return jsonify({'error': 'Missing files'}), 400

        hash_file = request.files['hash']
        wordlist_file = request.files['wordlist']

        task_id = str(uuid.uuid4())
        hash_path = f"/data/{task_id}_hash.txt"
        wordlist_path = f"/data/{task_id}_wordlist.txt"

        hash_file.save(hash_path)
        wordlist_file.save(wordlist_path)

        # Sanitasi hash dan wordlist
        with open(hash_path, 'r') as f:
            hash_content = f.read().strip()
        with open(hash_path, 'w') as f:
            f.write(hash_content + '\n')

        with open(wordlist_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]  # Hilangkan spasi dan baris kosong
        with open(wordlist_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

        r.set(task_id, '0')

        with open(wordlist_path) as f:
            lines = f.readlines()
            total_lines = len(lines)
            chunk_size = (total_lines + 3) // 4

            for i in range(4):
                start = i * chunk_size
                end = start + chunk_size
                chunk = lines[start:end]
                
                part_path = f"{UPLOAD_FOLDER}/{task_id}_part{i}.txt"
                with open(part_path, 'w') as part_file:
                    part_file.writelines(chunk)
                
                print(f"Part {i} contents: {''.join(chunk).strip()}")
                r.rpush('tasks', f"{task_id}:{i}")

        print("Files in /data:", os.listdir(UPLOAD_FOLDER))
        return jsonify({'task_id': task_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>')
def get_status(task_id):
    try:
        progress = r.get(task_id)
        if progress is None:
            progress = '0'
        else:
            progress = progress.decode()

        # Baca hasil dari file result
        result = ""
        for i in range(4):
            result_file = f"{UPLOAD_FOLDER}/{task_id}_result{i}.txt"
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        result += f"Part {i}: {content}\n"
        if not result:
            result = "Password not found in the provided wordlist."

        return jsonify({'progress': progress, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)