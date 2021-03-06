"""
next_backend dashboard.py
author: Lalit Jain, lalitkumarj@gmail.com
last updated: 2/11/15

Flask controller for dashboards. 
"""

from flask import Blueprint, Response, render_template, flash, request, redirect, url_for, session,jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
import requests, json
import next.utils as utils
from next.api.resource_manager import ResourceManager
import next.constants as constants
import next.database_client.PermStore as PermStore

# Declare this as dashboard blueprint
dashboard = Blueprint('dashboard', __name__, template_folder="templates", static_folder="static")
rm = ResourceManager()
db = PermStore.PermStore()

@dashboard.route('/experiment_list')
def experiment_list():
    """
    Endpoint that renders a page with a simple list of all experiments. 
    """
    # Experiments set
    experiments = []
    for app_id in rm.get_app_ids():
        for exp_uid in rm.get_app_exp_uids(app_id):
            start_date = rm.get_app_exp_uid_start_date(exp_uid)
            docs,didSucceed,message = db.getDocsByPattern("next_frontend_base", "keys", {'object_id':exp_uid, 'type':'exp'})
            print docs, didSucceed, message
            
            try:
                exp_key = docs[0]["_id"]
                experiments.append({'exp_uid': exp_uid, 'app_id':app_id, 'start_date':start_date, 'exp_key':exp_key})
            except IndexError as e:
                pass

    return render_template('experiment_list.html', experiments = reversed(experiments))

@dashboard.route('/system_monitor')
def system_monitor():
    """
    Endpoint that renders a page with a simple list of all monitoring. 
    """
    rabbit_url = "http://"+constants.NEXT_BACKEND_GLOBAL_HOST+":15672"
    cadvisor_url = "http://"+constants.NEXT_BACKEND_GLOBAL_HOST+":8888"
    mongodb_url = "http://"+constants.NEXT_BACKEND_GLOBAL_HOST+":28017"
    return render_template('system_monitor.html', rabbit_url=rabbit_url, cadvisor_url=cadvisor_url, mongodb_url=mongodb_url)

@dashboard.route('/experiment_dashboard/<exp_uid>/<app_id>/<exp_key>')
def experiment_dashboard(exp_uid, app_id, exp_key):
    """
    Endpoint that renders the experiment dashboard.

    Inputs: ::\n
    	(string) exp_uid, exp_uid for a current experiment.
    """
    # Not a particularly good way to do this. 
    alg_label_list = rm.get_algs_for_exp_uid(exp_uid)

    # Migrate this code to use keychain
    docs,didSucceed,message = db.getDocsByPattern("next_frontend_base", "keys", {'object_id':exp_uid, 'type':'perm'})
    perm_key = docs[0]["_id"]

    
    alg_list = [{'alg_label':alg["alg_label"], 'alg_label_clean':"_".join(alg["alg_label"].split())} for alg in alg_label_list]
    host_url = "http://"+constants.NEXT_BACKEND_GLOBAL_HOST+":"+constants.NEXT_BACKEND_GLOBAL_PORT
    
    return render_template(app_id+'.html', app_id = app_id, exp_uid = exp_uid, alg_list = alg_list, host_url=host_url, perm_key = perm_key)






