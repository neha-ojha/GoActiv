# These are the controllers for your ajax api.

import os
import sys
lib_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib/py/fitbit-0.2.4-py2.7.egg")
sys.path.append(lib_path)



import time
import datetime
from fitbit.api import FitbitOauth2Client
from fitbit import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
from requests_oauthlib import OAuth2Session
import requests

client_id = '227XNF'
client_secret = '1a53508ac0bd0aa5ffa3a9f6de07cb9d'
redirect_uri = ('https://%s/project/default/fitbit_auth' %
                request.env.http_host)

API_ENDPOINT = "https://api.fitbit.com"
refresh_token_url = "%s/oauth2/token" % API_ENDPOINT


def maybe_sync_data_from_fitbit():

    r = db(db.fitbit_user_t.user_email == auth.user.email).select(db.fitbit_user_t.ALL)

    if len(r) == 0:
        return False
    else:
        if time.time() > r[0].expires_at:
            oauth = OAuth2Session(client_id)

            token = oauth.refresh_token(
                        refresh_token_url,
                        refresh_token=r[0].refresh_token,
                        auth=requests.auth.HTTPBasicAuth(client_id, client_secret)
            )

            r = db(db.fitbit_user_t.user_email == auth.user.email).update(access_token = token["access_token"],
                                                                    refresh_token = token["refresh_token"],
                                                                    expires_at = token["expires_at"])
            r = db(db.fitbit_user_t.user_email == auth.user.email).select(db.fitbit_user_t.ALL)

        client = Fitbit(client_id, client_secret, access_token=r[0].access_token,
                        refresh_token=r[0].refresh_token)
        user = client.user_profile_get()

        act = client.activity_stats()
        steps = client.time_series(resource="activities/steps", period="7d")
        wt_goal = client.body_weight_goal()
        day = time.gmtime().tm_wday
        day_list = [0, 1, 2, 3, 4, 5, 6]
        new_day_list = day_list[day+1:] + day_list[:day+1]
        row_dict = {}
        row_dict["user_email"] = auth.user.email
        week_val = 0
        for idx, day in enumerate(new_day_list):
            step_val = int(steps['activities-steps'][idx]['value'])
            row_dict["d" + str(day)] = step_val
            week_val = week_val + step_val
        row_dict["week_total"] = week_val
        row_dict["lifetime"] = act["lifetime"]["total"]["steps"]
        row_dict["last_updated_day"] = day
        u = db.user_t(db.user_t.user_email == auth.user.email).update(weight=user["user"]["weight"],
                                                                       weight_target=wt_goal["goal"]["weight"])
        s = db.steps_t.update_or_insert((db.steps_t.user_email == auth.user.email),
                                        **row_dict)
        return True

@auth.requires_signature()
def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])

def get_user_list():
    pattern = request.vars.term
    my_friends = db(db.friends_t.user_email == auth.user.email)._select(db.friends_t.friend_email)
    selected = [row.user_email for row in db(~db.user_t.user_email.belongs(
                my_friends) 
                & db.user_t.user_email.contains(pattern))
                .select(db.user_t.ALL) if row.user_email != auth.user.email]
    return response.json(selected)
 
@auth.requires_signature()
def get_user_data():
    logged_in = True
    user_data_present = True
    user=None
    steps=None
    fitbit_linked = False

    if auth.user_id == None:
        logged_in = False
        user_data_present = False

    if logged_in == True:
        fitbit_linked = maybe_sync_data_from_fitbit()
        r = db(db.user_t.user_email == auth.user.email).select(db.user_t.ALL)
        s = db(db.steps_t.user_email == auth.user.email).select(db.steps_t.ALL)
        day = time.gmtime().tm_wday
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        db_week_steps = [0 for i in range(7)]

        weekdays = days[day+1:] + days[:day+1]
        today_s = 0
        week_avg_s = 0
        week_total_s = 0
        lifetime_s = 0
        if len(s) > 0:
            friend_s = get_today_weekly(s[0])
            today_s = friend_s["d" + str(day)]
            week_total_s = friend_s.week_total
            week_avg_s = friend_s.week_total / 7
            lifetime_s = friend_s.lifetime
            db_week_steps = [friend_s["d" + str(i)] for i in range(7)]


        week_steps= db_week_steps[day+1:] + db_week_steps[:day+1]
        steps = dict(
            day = day,
            today_s = today_s,
            week_total_s = week_total_s,
            week_avg_s = week_avg_s,
            lifetime_s = lifetime_s,
            weekdays = weekdays,
            week_steps = week_steps,
        )
        if len(r) == 0:
            user_data_present = False
        else:
            user_data_present = True
            user = dict(
                dob=r[0].dob,
                image=r[0].image,
                sex=r[0].sex,
                height=r[0].height,
                user_name=get_user_name_from_email(r[0].user_email),
                weight=r[0].weight,
                steps_target=r[0].steps_target,
                weight_target=r[0].weight_target,
            )

    return response.json(dict(
        user=user,
        logged_in = logged_in,
        user_data_present = user_data_present,
        steps=steps,
        fitbit_linked=fitbit_linked,

    ))

# Note that we need the URL to be signed, as this changes the db.
@auth.requires_signature()
def add_user_data():
    ret = db.user_t.update_or_insert((db.user_t.user_email==auth.user.email),
        user_email=auth.user.email,
        image=request.vars.image,
        dob=request.vars.dob,
        sex=request.vars.sex,
        height=request.vars.height,
        steps_target=request.vars.steps_target,
        weight_target=request.vars.weight_target,
        weight=request.vars.weight
    )
    day = time.gmtime().tm_wday 
    ret = db.steps_t.update_or_insert((db.steps_t.user_email==auth.user.email),
       user_email=auth.user.email,
       last_updated_day = day
    ) 
    r = db(db.user_t.user_email == auth.user.email).select(db.user_t.ALL)[0]
    user = dict(
        dob=r.dob,
        image=r.image,
        sex=r.sex,
        height=r.height,
        user_name=get_user_name_from_email(r.user_email),
        weight=r.weight,
        steps_target=r.steps_target,
        weight_target=r.weight_target
    )
    return response.json(dict(user=user, logged_in=True,
                          user_data_present=True, fitbit_linked=False))


@auth.requires_signature()
def add_steps_data():
  day = "d" + str(request.vars.day)
  steps = int(request.vars.steps)
  row_dict = {}
  s = db(db.steps_t.user_email == auth.user.email).select(db.steps_t.ALL)
 
  today = datetime.datetime.now()
  curr_day = time.gmtime().tm_wday
  diff_days = abs((today - s[0].updated_on).days)
  if diff_days > 7:
    diff_days = 7
  row_dict = s[0]
  day_num = range(7)
  for i in range(1, diff_days+1):
    idx = day_num[curr_day-i]
    row_dict["d" + str(idx)] = 0
 
  row_dict.lifetime = row_dict.lifetime - row_dict[day] + steps 
  row_dict[day] = steps
  
  row_dict["week_total"] = 0
  for i in day_num:
      row_dict["week_total"] = (row_dict["week_total"] +                                 row_dict["d" + str(i)])
  ret = db.steps_t.update_or_insert((db.steps_t.user_email ==
                                           auth.user.email),
                                             **row_dict)

@auth.requires_signature()
def add_friend():
  db.friends_t.insert(user_email=auth.user.email,
                      friend_email=request.vars.friend)

def accept_friend():
  db((db.friends_t.user_email==request.vars.friend) &
     (db.friends_t.friend_email==auth.user.email)).update(accepted=True)

def deny_friend():
  db((db.friends_t.user_email==request.vars.friend) &
     (db.friends_t.friend_email==auth.user.email)).delete()

@auth.requires_signature()
def get_friend_data():
  current_friends1 = [row.friend_email for row in
                         db((db.friends_t.user_email == auth.user.email) &
                         (db.friends_t.accepted == True)).select(
                         db.friends_t.ALL)]
  current_friends2 = [row.user_email for row in 
                      db((db.friends_t.friend_email == auth.user.email) &
                         (db.friends_t.accepted == True)).select(
                         db.friends_t.ALL)]
  current_friends = current_friends1 + current_friends2
                 
  pending_requests = [row.user_email for row in 
                      db((db.friends_t.friend_email == auth.user.email) &
                         (db.friends_t.accepted == False)).select(
                         db.friends_t.ALL)]
  pending_requests_data = [row for row in db().select(db.user_t.ALL)
                           if row.user_email in pending_requests]
  pending_friends = []
  friend_req = {}
  for row in pending_requests_data:
    friend_req["image"] = row.image
    friend_req["user_email"] = row.user_email
    friend_req["user_name"] = get_user_name_from_email(row.user_email)
    pending_friends.append(friend_req.copy())

  friend_rows = [row for row in db().select(
                 db.steps_t.ALL, orderby=db.steps_t.user_email)
                 if row.user_email in current_friends]
  user_rows = [row for row in db().select(
                 db.user_t.ALL, orderby=db.user_t.user_email)
                 if row.user_email in current_friends]
  friend_info = []
  friend_steps = {}
  day = time.gmtime().tm_wday
  day_col = "d" + str(day)
  for (idx, row) in enumerate(user_rows):
    friend_steps["user_email"] = row["user_email"]
    friend_steps["user_name"] = get_user_name_from_email(row.user_email)
    friend_steps["first_name"] = friend_steps["user_name"].split()[0]
    friend_steps["image"] = row.image
    friend_s = get_today_weekly(friend_rows[idx])
    friend_steps["today"] = friend_s[day_col]
    friend_steps["weekly"] = friend_s["week_total"] / 7
    friend_info.append(friend_steps.copy())

  return response.json(dict(friend_data=friend_info,
                            friend_requests=pending_friends))

def get_today_weekly(friend):
  today = datetime.datetime.now()
  diff_days = abs((today - friend.updated_on).days)
  curr_day = time.gmtime().tm_wday
  day_num = range(7)
  if diff_days > 7:
    diff_days = 7
  for i in range(1, diff_days+1):
    idx = day_num[curr_day-i]
    friend["d" + str(idx)] = 0

  friend["week_total"] = 0
  for i in day_num:
      friend["week_total"] = (friend["week_total"] +
                              friend["d" + str(i)])

  return friend
