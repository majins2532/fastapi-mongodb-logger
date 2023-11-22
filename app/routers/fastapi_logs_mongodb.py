from fastapi import APIRouter, Request, Response, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from core.dependencies import mdb as mdb_conn_local
from .utils import PATH_HTML, PATH_API
from core.mdbutils import mdb_connection as mdb_conn
from core.settings import API_TOKEN_KEY, MDB_DATABASE
from tempfile import NamedTemporaryFile
import pandas as pd
import os
import re
from datetime import datetime, tzinfo, timezone

_PATH_NF_LOGIN = f"/nf_login"
_PATH_NF_LOGIN_CHECK = f"/nf_login_check"
_PATH_NF_CARD_ITEMS = f"/nf_card_items"
_PATH_NF = f"/nf_log"

_NAME_LOGIN = "nf_login.html"
_NAME_ITEMS = "nf_card_items.html"
_NAME_LOGGER = "nf_log.html"

router = APIRouter(tags=["Logger"])

##### Logger in FastAPI
@router.get(_PATH_NF_LOGIN_CHECK, status_code=200)
def login_logger_check(token:str):
    if not token:
        return False
    if token != API_TOKEN_KEY:
        return False
    return True

@router.get(_PATH_NF_LOGIN, response_class=HTMLResponse, status_code=200)
def login_logger(request: Request):
    cookie_login_key = request.cookies.get('login_key')
    if cookie_login_key:
        if cookie_login_key == API_TOKEN_KEY:
            return RedirectResponse(url=PATH_API+_PATH_NF_CARD_ITEMS, status_code=303)
    with open(PATH_HTML+_NAME_LOGIN, 'r') as file:
        html_content = file.read()
    modified_html = html_content.replace('{ url_web }', f'{PATH_API+_PATH_NF_CARD_ITEMS}')
    modified_html2 = modified_html.replace('{ check_token }', f'{PATH_API+_PATH_NF_LOGIN_CHECK}')
    return modified_html2

@router.get(_PATH_NF_CARD_ITEMS, response_class=HTMLResponse, status_code=200)
def read_mongodb_log_card_items(request: Request):
    cookie_login_key = request.cookies.get('login_key')
    if not cookie_login_key:
        return RedirectResponse(url=PATH_API+_PATH_NF_LOGIN, status_code=303)
    if cookie_login_key != API_TOKEN_KEY:
        return RedirectResponse(url=PATH_API+_PATH_NF_LOGIN, status_code=303)
    cols = mdb_conn_local.list_collections()
    html_items = ""
    for col in cols:
        html_items += f"""
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{col}</h5>
                        <p class="card-text">Description for {col}</p>
                        <a href="{PATH_API}{_PATH_NF}?db={col}" class="btn btn-primary">Connect</a>
                    </div>
                </div>
            </div>
        """
    with open(PATH_HTML+_NAME_ITEMS, 'r') as file:
        html_content = file.read()
    modified_html = html_content.replace('{items}', html_items)
    return modified_html

@router.get(_PATH_NF, response_class=HTMLResponse, status_code=200)
def read_mongodb_log_netforce(request: Request, db:str | None = None, message: str | None = None, details: str | None = None, date_from: str | None = None, date_to: str | None = None):
    cookie_login_key = request.cookies.get('login_key')
    if not cookie_login_key:
        return RedirectResponse(url=PATH_API+_PATH_NF_LOGIN, status_code=303)
    if cookie_login_key != API_TOKEN_KEY:
        return RedirectResponse(url=PATH_API+_PATH_NF_LOGIN, status_code=303)
    date_format = "%Y-%m-%d %H:%M:%S"
    start_date = None
    end_date = None
    if date_from:
        date_from = date_from + " 00:00:00"
        start_date = datetime.strptime(date_from, date_format)
        start_date.replace(tzinfo=timezone.utc)
        #start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    if date_to:
        date_to = date_to + " 23:59:59"
        end_date = datetime.strptime(date_to, date_format)
        end_date.replace(tzinfo=timezone.utc)
        #end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    query = {}
    if message and details:
        query["message"] = {'$regex': message}
        query["details"] = {'$regex': details}
    elif not details and message:
        query["message"] = {'$regex': message}
    elif details and not message:
        query["details"] = {'$regex': details}
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date and not end_date:
        query["date"] = {'$gte': start_date}
    elif not start_date and end_date:
        query["date"] = {'$lte': end_date}
    print(query)
    sort=list({
        'date': -1
    }.items())
    mdb = mdb_conn()
    mdb.connect(MDB_DATABASE)
    mdb.connect_table(db)
    logs = mdb.find_new(query,None,200)
    html_item = ""
    for item in logs:
        detail = str(item['details']).replace('"',"'")
        html_item += '{_id: "%s", message: "%s", date: "%s", user_id: "%s", ip_addr: "%s", details: "%s"},' % (str(item["_id"]),item['message'],item['date'],item['user_id'],item['ip_addr'],detail)
    with open(PATH_HTML+_NAME_LOGGER, 'r') as file:
        html_content = file.read()
    modified_html = html_content.replace('{ items }', html_item)
    modified_html2 = modified_html.replace('{ UrlHome }', PATH_API+_PATH_NF_CARD_ITEMS)
    mdb.disconnect_table()
    mdb.disconnect()
    return modified_html2

@router.get("/download_excel")
def download_excel(response: Response, db:str | None = None, message: str | None = None, details: str | None = None, date_from: str | None = None, date_to: str | None = None):
    res = {}
    date_format = "%Y-%m-%d %H:%M:%S"
    start_date = None
    end_date = None
    if date_from:
        date_from = date_from + " 00:00:00"
        start_date = datetime.strptime(date_from, date_format)
        start_date.replace(tzinfo=timezone.utc)
    if date_to:
        date_to = date_to + " 23:59:59"
        end_date = datetime.strptime(date_to, date_format)
        end_date.replace(tzinfo=timezone.utc)
    query = {}
    if message and details:
        query["message"] = {'$regex': message}
        query["details"] = {'$regex': details}
    elif not details and message:
        query["message"] = {'$regex': message}
    elif details and not message:
        query["details"] = {'$regex': details}
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date and not end_date:
        query["date"] = {'$gte': start_date}
    elif not start_date and end_date:
        query["date"] = {'$lte': end_date}
    mdb = mdb_conn()
    mdb.connect(MDB_DATABASE)
    mdb.connect_table(db)
    datas = mdb.find(query,200)
    res["_id"] = []
    res["date"] = []
    res["user_id"] = []
    res["related_id"] = []
    res["ip_addr"] = []
    res["message"] = []
    res["details"] = []
    for data in datas:
        res["_id"].append(str(data["_id"]) or "")
        res["date"].append(data["date"] or "")
        res["user_id"].append(int(data["user_id"]) or "")
        res["related_id"].append(data["related_id"] or "")
        res["ip_addr"].append(data["ip_addr"] or "")
        res["message"].append(data["message"] or "")
        res["details"].append(str(data["details"]) or "")
    excel_file_path = create_excel(res)
    mdb.disconnect_table()
    mdb.disconnect()
    if not os.path.exists(excel_file_path):
        return {"error": "File not found"}
    return FileResponse(excel_file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="export.xlsx")

def create_excel(data):
    df = pd.DataFrame(data)
    file_path = '/tmp/sample_data.xlsx'
    df.to_excel(file_path, index=False)
    print(f"Excel file '{file_path}' created successfully.")
    return file_path