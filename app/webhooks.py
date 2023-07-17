from flask import Flask, request, jsonify
import re
import jsonpatch
import base64

warden = Flask(__name__)

#POST route for Admission Controller
@warden.route('/validate', methods=['POST'])
#Admission Control Logic - validating
def validating_webhook():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")

    print("\n\n\n\n\n", "HERE IS THE REQUEST INFO", request_info, "\n\n\n\n\n\n")

    stoof = request_info["request"]["object"]["metadata"]["namespace"]
    check = "busybox"

    if stoof != check:
        #Send response back to controller if validations succeeds
        return k8s_response(False, uid, "Busybox namespace does not exists")

    try:
        if request_info["request"]["object"]["spec"]["containers"][0]["image"] == "busybox:latest":
            return k8s_response(True, uid, "latest tag exists")
    except:
        return k8s_response(False, uid, "No Tag exist. A busybox latest tag is required")

    #Send response back to controller if failed
    return k8s_response(False, uid, "Not allowed without a busybox latest tag")

    # Code for validating webhook HERE

# CHAT GPT CODE START

    # namespace = request_info["request"]["namespace"]
    # containers = request_info["request"]["object"]["spec"]["containers"]

    # # Check if the namespace is 'busybox'
    # if namespace != "busybox":
    #     return jsonify({"allowed": False, "uid": uid, "message": "Only pods in the busybox namespace are allowed"})

    # # Check if any container's image isn't 'busybox:latest'
    # for container in containers:
    #     image = container["image"]
    #     if image != "busybox:latest":
    #         return jsonify({"allowed": False, "uid": uid, "message": "Only containers with the image 'busybox:latest' are allowed"})

    # # If all checks pass, allow the pod
    # return jsonify({"allowed": True, "uid": uid})

# if __name__ == "__main__":
#     warden.run(port=8000)

# CHAT GPT CODE END

#Function to respond back to the Admission Controller
def k8s_response(allowed, uid, message):
     return jsonify({"apiVersion": "admission.k8s.io/v1", "kind": "AdmissionReview", "response": {"allowed": allowed, "uid": uid, "status": {"message": message}}})

#Function to respond back to the Admission Controller
def k8s_response_mutate(allowed, uid, message):
     print("Mutating will now occur since the tag is not latest")
     return jsonify({"apiVersion": "admission.k8s.io/v1", "kind": "AdmissionReview", "response": {"allowed": allowed, "uid": uid, "status": {"message": message}}})

#POST route for Admission Controller
@warden.route("/mutate", methods=["POST"])
#Admission Control Logic - mutating
def mutatating_webhook():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")

    print("Testing if webhook can be called")

    print("\n\n\n\n\n", "HERE IS THE REQUEST INFO", request_info, "\n\n\n\n\n\n")

    stoof = request_info["request"]["object"]["metadata"]["namespace"]
    check = "busybox"

    # Code for mutating webhook HERE

    tag = request_info["request"]["object"]["spec"]["containers"][0]["image"]
    print(tag)
    substring_image = tag.split(':')[0]
    substring_latest = tag.split(':')[1]

    if stoof != check:
        #Send response back to controller if validations succeeds
        return k8s_response(False, uid, "Busybox namespace does not exist exists")

    try:
        if substring_image == "busybox":
            if substring_latest == "latest":
                return k8s_response(True, uid, "latest tag exists")
    except:
        return k8s_response_mutate(False, uid, "No tag exist. A busybox latest tag is required, this will be fixed")

    #Send response back to controller if failed
    return k8s_response_mutate(False, uid, "Not allowed without a busybox latest tag, this will be fixed")

if __name__ == '__main__':
    warden.run(ssl_context=('certs/wardencrt.pem', 'certs/wardenkey.pem'),debug=True, host='0.0.0.0')
