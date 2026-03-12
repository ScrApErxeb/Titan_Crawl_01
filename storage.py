# storage.py

import os
import json

# Optionnel : boto3 si S3 est utilisé
try:
    import boto3
except ImportError:
    boto3 = None


class BaseStorage:
    """Interface pour tous les systèmes de stockage"""
    def save(self, data: dict):
        raise NotImplementedError("save doit être implémenté")


class FileStorage(BaseStorage):
    """Stocke les données localement au format JSON"""
    def __init__(self, path="data"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def save(self, data: dict):
        filename = f"{self.path}/{data['url'].replace('://','_').replace('/','_')}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[STORAGE] Saved: {filename}")
        except Exception as e:
            print(f"[ERROR] Saving {filename}: {e}")


class S3Storage(BaseStorage):
    """Stocke les données sur AWS S3 ou compatible"""
    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        if not boto3:
            raise RuntimeError("boto3 non installé, impossible d'utiliser S3Storage")
        self.bucket = bucket_name
        self.s3 = boto3.client("s3", region_name=region_name)

    def save(self, data: dict):
        key = f"{data['url'].replace('://','_').replace('/','_')}.json"
        try:
            self.s3.put_object(Bucket=self.bucket,
                               Key=key,
                               Body=json.dumps(data, ensure_ascii=False),
                               ContentType="application/json")
            print(f"[STORAGE] Saved to S3: {key}")
        except Exception as e:
            print(f"[ERROR] Saving to S3 {key}: {e}")