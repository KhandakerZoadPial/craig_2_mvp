from datetime import datetime



def generate_response(status="undefined", code=0, data={}, error={}):
    sample_response = {
        "status": status,
        "code": code,
        "data": data,
        "error": error,
        "meta": {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    return sample_response