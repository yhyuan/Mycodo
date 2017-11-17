# -*- coding: utf-8 -*-
import logging
import requests
import sqlalchemy

from flask import flash
from flask import redirect
from flask import url_for

from mycodo.mycodo_flask.extensions import db
from flask_babel import gettext

from mycodo.mycodo_flask.utils import utils_general

from mycodo.databases.models import DisplayOrder
from mycodo.databases.models import Remote
from mycodo.utils.system_pi import csv_to_list_of_int
from mycodo.utils.system_pi import list_to_csv

from mycodo.mycodo_flask.utils.utils_general import add_display_order
from mycodo.mycodo_flask.utils.utils_general import delete_entry_with_id
from mycodo.mycodo_flask.utils.utils_general import flash_form_errors

from mycodo.config import STORED_SSL_CERTIFICATE_PATH

logger = logging.getLogger(__name__)


#
# Authenticate remote hosts
#


def auth_credentials(address, user, password_hash):
    credentials = {
        'user': user,
        'pw_hash': password_hash
    }
    url = 'https://{add}/auth/'.format(
        add=address, hash=password_hash, user=user)
    certificate = '{path}/{file}'.format(path=STORED_SSL_CERTIFICATE_PATH,
                                         file='{add}_cert.pem'.format(
                                            add=address))
    try:
        # import urllib3
        # url_test = 'https://{add}/auth/?pw_hash={hash}&user={user}'.format(
        #     add=address, hash=password_hash, user=user)
        # http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
        #                            ca_certs=certificate,
        #                            assert_hostname=False)
        # r = http.request('GET', url_test)
        # logger.error("STATUS:", r.text)
        # logger.error("Certificate verification NO HOSTNAME successful")

        r = requests.get(url, params=credentials, verify=False)
        return int(r.text)
    except Exception as e:
        logger.exception(
            "'auth_credentials' raised an exception: {err}".format(err=e))
        return 1


def check_new_credentials(address, user, passw):
    """
    Authenticate a remote Mycodo install that will be used in this system's
    Remote Admin dashboard.
    The user name and password is sent, and if verified, the password hash
    and SSL certificate is sent back.
    The hash is used to authenticate and the certificate is used to perform
    a verified SSL in subsequent connections.
    """
    credentials = {
        'user': user,
        'passw': passw
    }
    url = 'https://{}/newremote/'.format(address)
    try:
        r = requests.get(url, params=credentials, verify=False)
        return r.json()
    except Exception as msg:
        return {
            'status': 1,
            'message': "Error connecting to host: {err}".format(err=msg),
            'certificate': None
        }


def remote_get_inputs(address, user, password_hash):
    credentials = {
        'user': user,
        'pw_hash': password_hash
    }
    url = 'https://{add}/remote_get_inputs/'.format(add=address)
    try:
        r = requests.get(url, params=credentials, verify=False)
        return r.text
    except Exception as e:
        logger.exception(
            "'remote_get_inputs' raised an exception: {err}".format(err=e))
        return 1


def remote_host_add(form_setup, display_order):
    if not utils_general.user_has_permission('edit_settings'):
        return redirect(url_for('general_routes.home'))

    if form_setup.validate():
        try:
            pw_check = check_new_credentials(form_setup.host.data,
                                             form_setup.username.data,
                                             form_setup.password.data)
            if pw_check['status']:
                flash(pw_check['message'], "error")
                return 1

            # Write remote certificate to file
            public_key = '{path}/{file}'.format(path=STORED_SSL_CERTIFICATE_PATH,
                                                file='{add}_cert.pem'.format(
                                                    add=form_setup.host.data))

            flash(pw_check['certificate'], "error")

            file_handler = open(public_key, 'w')
            file_handler.write(pw_check['certificate'])
            file_handler.close()

            new_remote_host = Remote()
            new_remote_host.host = form_setup.host.data
            new_remote_host.username = form_setup.username.data
            new_remote_host.password_hash = pw_check['message']
            try:
                db.session.add(new_remote_host)
                db.session.commit()
                flash(gettext(u"Remote Host %(host)s with ID %(id)s (%(uuid)s)"
                              u" successfully added",
                              host=form_setup.host.data,
                              id=new_remote_host.id,
                              uuid=new_remote_host.unique_id),
                      "success")

                DisplayOrder.query.first().remote_host = add_display_order(
                    display_order, new_remote_host.id)
                db.session.commit()
            except sqlalchemy.exc.OperationalError as except_msg:
                flash(gettext(u"Remote Host Error: %(msg)s", msg=except_msg),
                      "error")
            except sqlalchemy.exc.IntegrityError as except_msg:
                flash(gettext(u"Remote Host Error: %(msg)s", msg=except_msg),
                      "error")
        except Exception as except_msg:
            flash(gettext(u"Remote Host Error: %(msg)s", msg=except_msg),
                  "error")
    else:
        flash_form_errors(form_setup)


def remote_host_del(form_setup):
    if not utils_general.user_has_permission('edit_settings'):
        return redirect(url_for('general_routes.home'))

    try:
        delete_entry_with_id(Remote,
                             form_setup.remote_id.data)
        display_order = csv_to_list_of_int(DisplayOrder.query.first().remote_host)
        display_order.remove(int(form_setup.remote_id.data))
        DisplayOrder.query.first().remote_host = list_to_csv(display_order)
        db.session.commit()
    except Exception as except_msg:
        flash(gettext(u"Remote Host Error: %(msg)s", msg=except_msg), "error")
