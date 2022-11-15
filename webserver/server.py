#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,session
from collections import defaultdict

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "hl3648"
DB_PASSWORD = "7249"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")




@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index(methods=['Get','POST']):
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  
  #
  # example of a database query
  #


    #user.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #



  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/mainpage')
def mainpage():
  users = g.conn.execute("SELECT * FROM Users")
  user = []
  #for users in user
  for result in users:
    user.append((result[0],result[1],result[2],result[3],result[4]))  # can also be accessed using result[0]
    # for user in users:
    # names.append(user['user_name'])
  users.close()
  follows = g.conn.execute("""SELECT DISTINCT U.user_name, F.store_id, C.name FROM Users as U, Follow as F, Own_stores as O, Conglomerates as C WHERE U.user_id = F.user_id AND F.store_id = O.store_id AND F.conglomerate_id = C.conglomerate_id""")
  fo = []
  for f in follows:
    fo.append((f[0],f[1],f[2]))
  follows.close()
  context = dict(data = user,fo=fo)

  return render_template("mainpage.html",**context)

@app.route('/info')
def info():
  return render_template("info.html")

@app.route('/conglomerates')
def conglomerates():
  cursor = g.conn.execute("SELECT * FROM Conglomerates")
  cong = []
  for c in cursor:
    cong.append((c[1],c[2]))
  cursor.close()
  
  stores = g.conn.execute("""SELECT DISTINCT O.store_id, O.business_building, O.business_address_unit, O.business_street, O.city, O.zip, O.conglomerate_id, C.name FROM Conglomerates as C, Own_stores as O WHERE C.conglomerate_id = O.conglomerate_id""")
  sto = []
  for store in stores:
    sto.append((store[0],store[1],store[2],store[3],store[4],store[5],store[6],store[7]))
  context = dict(data=cong,store=sto)
  return render_template("conglomerates.html", **context)

@app.route('/mediation')
def mediation():
  cursor = g.conn.execute("SELECT * FROM Mediators")
  mediators = []
  for c in cursor:
    mediators.append((c[1],c[2],c[3]))
  cursor.close()

  hiring = g.conn.execute("""SELECT DISTINCT C.name, M.mediator_name FROM Hire as H, Mediators as M, Conglomerates as C WHERE H.mediator_id = M.mediator_id AND H.conglomerate_id = C.conglomerate_id""")
  hires = []
  for h in hiring:
    hires.append((h[0],h[1]))
  hiring.close()

  ins = g.conn.execute("""SELECT DISTINCT * FROM Initiate as I, Mediators as M, Mediations_resolve as R WHERE I.mediator_id = M.mediator_id AND I.mediation_id = R.mediation_id""")
  inits = []
  for i in ins:
    inits.append((i[1],i[3],i[7],i[8],i[9],i[10],i[11]))
  ins.close()
  context = dict(data=mediators,hires=hires,ins=inits)
  return render_template("mediation.html", **context)

@app.route('/complaints')
def complaints():
    complains = g.conn.execute("SELECT * FROM Complaints_make_about")
    coms = []
    for c in complains:
        coms.append((c[0],c[1],c[2],c[3],c[4],c[5]))
    complains.close()

    user_complains = g.conn.execute("""SELECT Distinct U.user_name, A.complaint_id, COUNT(distinct c.comment_id) FROM Users as U, Complaints_make_about as A, Comments_post_under as C WHERE U.user_id = A.user_id AND U.user_id = C.user_id GROUP BY A.complaint_id, U.user_id, c.comment_id""")
    uc = []
    for u in user_complains:
        uc.append((u[0],u[1],u[2]))
    user_complains.close()
    context = dict(data=coms,uc=uc)
    return render_template("complaints.html",**context)

#Make a complaint
@app.route('/complain', methods=['POST'])
def complain():
  complain = request.form['complain']
  print(complain)
  #cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
  return redirect('/complaints')

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
  g.conn.execute(text(cmd), name1 = name, name2 = name)
  return redirect('/')


@app.route('/login', methods=['Get','POST'])
def login():
    if request.method == 'POST':
        Username = request.form['Username']
        Email = request.form['Username']
        Age = request.form['Age']
        Zip = request.form['Zip']

        valid_users = g.conn.execute("SELECT user_name FROM Users")

        user = g.conn.execute(
                'SELECT * FROM user WHERE user_name = ?', (Username,)
            ).fetchone()

        print(user)

        if user is None:
            error = 'Incorrect username.'
        
        if error is None:
                # session.clear()
                # session['user_id'] = user['id']
                return redirect(mainpage.html)
    
    return render_template('/index.html')
    
    

    

    # users = []

    # for u in valid_users:
    #     users.append(u['user_name'])
    # print(users)
    # if Username in users:
    #     return render_template('mainpage.html')
    
    return redirect('/')
    


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()