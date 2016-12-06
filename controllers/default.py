# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import os
import sys
lib_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib/py/fitbit-0.2.4-py2.7.egg")
sys.path.append(lib_path)

from fitbit.api import FitbitOauth2Client
from fitbit import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
from requests_oauthlib import OAuth2Session

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def fitbit_auth():
    token = None
    error = None

    client_id = '227XNF'
    client_secret = '1a53508ac0bd0aa5ffa3a9f6de07cb9d'
    redirect_uri = ('https://%s/project/default/fitbit_auth' %
                     request.env.http_host)
    code =  request.vars.code

    oauth = FitbitOauth2Client(client_id, client_secret)

    print code
    try:
        token = oauth.fetch_access_token(code, redirect_uri)
    except MissingTokenError:
        error = 'Missing access token parameter.</br>Please check that you are using the correct client_secret'
    except MismatchingStateError:
        error ='CSRF Warning! Mismatching state'
    print token

    client = Fitbit(client_id, client_secret, access_token=token["access_token"], refresh_token=token["refresh_token"])

    f_id = db.fitbit_user_t.insert(
        user_email=auth.user.email,
        fitbit_user_id=token["user_id"],
        access_token=token["access_token"],
        refresh_token=token["refresh_token"],
        expires_at=token["expires_at"],
    )
    user = client.user_profile_get()
    goals = client.activities_daily_goal()
    wt_goal = client.body_weight_goal()
    print wt_goal
    u_id = db.user_t.insert(
        user_email=auth.user.email,
        dob=user["user"]["dateOfBirth"],
        sex=user["user"]["gender"],
        height=user["user"]["height"],
        image=user["user"]["avatar150"],
        steps_target=goals["goals"]["steps"],
        weight_target=wt_goal["goal"]["weight"],
        weight=user["user"]["weight"],
    )


    redirect(URL('index'))


