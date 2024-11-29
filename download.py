import os
from datetime import date, timedelta, datetime
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import zipfile
import shutil

# copernicus_user = os.getenv("COPERNICUS_TOKEN").strip() # copernicus User
# copernicus_password = os.getenv("COPERNICUS_SECRET").strip() # copernicus Password
copernicus_user = "muhbader70@gmail.com"
copernicus_password = "vye1uab.dcm*PNQ!zfv"
root_dir = "/data"

logs = f"{root_dir}/logs.txt"
with open(logs, "a") as log:
    log.write(f"{copernicus_user}\n")
    log.write(f"{copernicus_password}\n")


# WKT Representation of BBOX
ft = "POLYGON ((-123.1454969332428 49.30196348364174, -123.1454969332428 49.21421911729337, -122.99313469145733 49.21421911729337, -122.99313469145733 49.30196348364174, -123.1454969332428 49.30196348364174))"
data_collection = "SENTINEL-2" # Sentinel satellite
cloudCover = 30

today =  datetime(2024, 11, 27)
today_string = today.strftime("%Y-%m-%d")
yesterday = today - timedelta(days=1000)
yesterday_string = yesterday.strftime("%Y-%m-%d")

if not os.path.exists(f"{root_dir}/files"):
    os.mkdir(f"{root_dir}/files")

if not os.path.exists(f"{root_dir}/sentinel_images"):
    os.mkdir(f"{root_dir}/sentinel_images")

def get_keycloak(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]


link = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloudCover:.2f}) and OData.CSC.Intersects(area=geography'SRID=4326;{ft}') and ContentDate/Start gt {yesterday_string}T00:00:00.000Z and ContentDate/Start lt {today_string}T00:00:00.000Z&$count=True&$top=100"

with open(logs, "a") as log:
    log.write(f"{link}\n")

json_ = requests.get(link).json()

p = pd.DataFrame.from_dict(json_["value"]) # Fetch available dataset
if p.shape[0] > 0 :
    p["geometry"] = p["GeoFootprint"].apply(shape)
    productDF = gpd.GeoDataFrame(p).set_geometry("geometry") # Convert PD to GPD
    productDF = productDF[~productDF["Name"].str.contains("L1C")] # Remove L1C dataset
    with open(logs, "a") as log:
        log.write(f" Total L2A tiles found {len(productDF)}\n")

    productDF["identifier"] = productDF["Name"].str.split(".").str[0]
    allfeat = len(productDF) 

    if allfeat == 0:
        with open(logs, "a") as log:
            log.write(f"No tiles found for {today} : {yesterday}\n")
    else:
        ## download all tiles from server
        for index,feat in enumerate(productDF.iterfeatures()):
            try:
                session = requests.Session()
                keycloak_token = get_keycloak(copernicus_user,copernicus_password)
                session.headers.update({"Authorization": f"Bearer {keycloak_token}"})
                url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({feat['properties']['Id']})/$value"
                response = session.get(url, allow_redirects=False)
                while response.status_code in (301, 302, 303, 307):
                    url = response.headers["Location"]
                    response = session.get(url, allow_redirects=False)
                
                with open(logs, "a") as log:
                    log.write("id: " + feat["properties"]["Id"]+"\n")

                file = session.get(url, verify=False, allow_redirects=True, stream=True)
                identifier = feat['properties']['identifier']
                with open(
                    f"{root_dir}/files/{identifier}.zip", #location to save zip from copernicus 
                    "wb",
                ) as p:
                    with open(logs, "a") as log:
                        log.write(feat["properties"]["Name"]+"\n")
                    p.write(file.content)

                
                file_name = f"{identifier}.SAFE/{identifier}-ql.jpg"
                with zipfile.ZipFile(os.path.join(f"{root_dir}/files", f"{identifier}.zip"), 'r') as zip_ref:
                    if file_name in zip_ref.namelist():
                        with open(logs, "a") as log:
                            log.write(f"found - {file_name}")
                        
                        zip_ref.extract(file_name,f"{root_dir}/sentinel_images",None)
                        shutil.move(f"{root_dir}/sentinel_images/{file_name}", f"{root_dir}/sentinel_images")
                        os.rmdir(f"{root_dir}/sentinel_images/{identifier}.SAFE")

            except:
                with open(logs, "a") as log:
                    log.write("problem with server")
else :
    with open(logs, "a") as log:
        log.write('no data found')


# Extracting zip files

# for zip_file in os.listdir(f"{root_dir}/files"):
#     if zip_file.endswith(".zip"):
#         file_name_raw = zip_file.split(".")[0]
#         with zipfile.ZipFile(os.path.join(f"{root_dir}/files", zip_file), 'r') as zip_ref:
            
#             # print(zip_ref.namelist())
#             file_name = f"{file_name_raw}.SAFE/{file_name_raw}-ql.jpg"
#             if file_name in zip_ref.namelist():
#                 print("found")
#                 zip_ref.extract(file_name,f"{root_dir}/sentinel_images",None)
#                 shutil.move(f"{root_dir}/sentinel_images/{file_name}", "{root_dir}/sentinel_images")
#                 os.rmdir(f"{root_dir}/sentinel_images/{file_name_raw}.SAFE")


import time
if not os.path.exists(f"{root_dir}/waiting"):
    os.mkdir(f"{root_dir}/waiting")
c = 0
while True:
    time.sleep(15)
    os.system(f"echo {c} >  {root_dir}/waiting/{c}.txt")
    c+=1
