import os
import hashlib
import pickle
import sys

VCS_DIR = '.vcs_storage'
HEAD_FILE = os.path.join(VCS_DIR, 'HEAD')

def init_vcs():
    os.makedirs(VCS_DIR, exist_ok=True)
    with open(HEAD_FILE, 'wb') as f:
        pickle.dump({}, f)
    print("VCS initialized.")

def hash_file_content(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def snapshot(directory, message="Snapshot"):
    snapshot_hash = hashlib.sha256()
    snapshot_data = {'files': {}, 'message': message}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if VCS_DIR in os.path.join(root, file):
                continue
            file_path = os.path.join(root, file)
            content_hash = hash_file_content(file_path)
            snapshot_data['files'][file_path] = content_hash
            snapshot_hash.update(content_hash.encode())
    
    hash_digest = snapshot_hash.hexdigest()
    with open(os.path.join(VCS_DIR, hash_digest), 'wb') as f:
        pickle.dump(snapshot_data, f)

    with open(HEAD_FILE, 'rb') as f:
        head = pickle.load(f)
    head[hash_digest] = message
    with open(HEAD_FILE, 'wb') as f:
        pickle.dump(head, f)

    print(f"Snapshot created with hash {hash_digest} and message: {message}")

def revert_to_snapshot(hash_digest):
    snapshot_path = os.path.join(VCS_DIR, hash_digest)
    if not os.path.exists(snapshot_path):
        print("Snapshot does not exist.")
        return
    
    with open(snapshot_path, 'rb') as f:
        snapshot_data = pickle.load(f)
    
    for file_path, content_hash in snapshot_data['files'].items():
        with open(file_path, 'wb') as f:
            f.write(content_hash.encode())
    
    current_files = set()
    for root, dirs, files in os.walk('.', topdown=True):
        if VCS_DIR in root:
            continue
        for file in files:
            current_files.add(os.path.join(root, file))
    
    snapshot_files = set(snapshot_data['files'].keys())
    files_to_delete = current_files - snapshot_files
    
    for file_path in files_to_delete:
        os.remove(file_path)
        print(f"Removed {file_path}")
    
    print(f"Reverted to snapshot {hash_digest}")

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "init":
        init_vcs()
    elif command == "snapshot":
        message = sys.argv[2] if len(sys.argv) > 2 else "Snapshot"
        snapshot('.', message)
    elif command == "revert":
        revert_to_snapshot(sys.argv[2])
    else:
        print
