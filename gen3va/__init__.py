"""Configures the application at server startup.
"""

from flask import Flask, session as flask_session
from flask.ext.cors import CORS
from flask.ext.login import LoginManager, user_logged_out

from gen3va.config import Config
from substrate import User, db as substrate_db
from gen3va.database import mongo

app = Flask(__name__,
            static_url_path=Config.BASE_URL + '/static',
            static_folder='static')


app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = Config.SQLALCHEMY_POOL_RECYCLE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 6
app.config['MONGO_URI'] = Config.MONGO_URI

substrate_db.init_app(app)
mongo.init_app(app)
cors = CORS(app)


# User authentication and sessioning.
# ----------------------------------------------------------------------------
# Change this SECRET_KEY to force all users to re-authenticate.
app.secret_key = 'CHANGE THIS IN THE FUTURE'


# @app.before_request
# def make_session_permanent():
#     """Sets Flask session to 'permanent', meaning 31 days.
#     """
#     flask_session.permanent = True


# Setup endpoints (Flask Blueprints)
# ----------------------------------------------------------------------------
# Import these after connecting to the DB.
from gen3va import endpoints
from gen3va.utils.jinjafilters import jinjafilters

# app.register_blueprint(endpoints.admin_pages)
# app.register_blueprint(endpoints.auth_pages)
app.register_blueprint(endpoints.error_page)
app.register_blueprint(endpoints.menu_pages)
app.register_blueprint(endpoints.report_pages)
app.register_blueprint(endpoints.signature_pages)
# app.register_blueprint(endpoints.tag_pages)
# app.register_blueprint(endpoints.download_api)
# app.register_blueprint(endpoints.upload_api)
app.register_blueprint(endpoints.signature_external_redirect_api)
app.register_blueprint(endpoints.signature_api)
app.register_blueprint(jinjafilters)


# Build all reports on starting the app
from substrate import Tag
from gen3va import database, report_builder
@app.before_first_request
def build_all_reports():
    # Get all tags 
    # tags = database.get_all(Tag)
    # print len([tag.name for tag in tags])
    # for tag in tags:
    #     if tag.name.startswith('BRD-'):
    #         report_builder.build(tag, category='cell')

    # Count tags with incomplete reports
    # c = 0
    # for tag in tags:
    #     report = tag.approved_report
    #     if report is None:
    #         c += 1
    #     else:
    #         if not report.complete(Config.SUPPORTED_ENRICHR_LIBRARIES):
    #             c += 1
    # print 'Number of tags with incomplete reports: %d' % c
    # Rebuild
    # for tag in tags:
    #     report = tag.approved_report
    #     if report is None:
    #         report_builder.build(tag, category='cell')
            # report_builder.rebuild(tag, category='cell', wait_till_done=True)
        # else:
        #     if not report.complete(Config.SUPPORTED_ENRICHR_LIBRARIES):
        #         report_builder.rebuild(tag, category='cell', wait_till_done=True)
    return

# User authentication
# ----------------------------------------------------------------------------
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'auth_pages.login'


# @login_manager.user_loader
# def load_user(user_id):
#     """Utility method for loading User for Flask-Login.
#     """
#     user = substrate_db.session.query(User).get(user_id)
#     app.config.user = user
#     return user

# @user_logged_out.connect_via(app)
# def unset_current_user(sender, user):
#     """When the user logs out, we need to unset this global variable.
#     """
#     app.config.user = None


# Setup global variables that are available in Jinja2 templates
# ----------------------------------------------------------------------------
app.config.update({
    'BASE_URL': Config.BASE_URL,
    'REPORT_URL': Config.REPORT_URL,
    'RESULTS_URL': Config.RESULTS_URL,
    'APPROVED_REPORT_URL': Config.APPROVED_REPORT_URL,
    'CUSTOM_REPORT_URL': Config.CUSTOM_REPORT_URL,
    'TAG_URL': Config.TAG_URL,
    'SIG_URL': Config.SIG_URL,
})
