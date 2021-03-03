#!/usr/bin/env python
# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, c
import ckan.lib.helpers as h
import ckan.lib.formatters as formatters
import json
import collections
from ckan.lib.search import make_connection
import logging
from ckanapi import LocalCKAN, NotFound, NotAuthorized

from ckanext.thai_gdc.model.opend import OpendModel

#from ckanext.pages import db

get_action = logic.get_action
opend_model = OpendModel()

log = logging.getLogger(__name__)

def get_organizations(all_fields=False, include_dataset_count=False, sort="name asc"):
    context = {'user': c.user}
    data_dict = {
        'all_fields': all_fields,
        'include_dataset_count': include_dataset_count,
        'sort': sort}
    return logic.get_action('organization_list')(context, data_dict)

def get_groups(all_fields=False, include_dataset_count=False, sort="name asc"):
    context = {'user': c.user}
    data_dict = {
        'all_fields': all_fields,
        'include_dataset_count': include_dataset_count,
        'sort': sort}
    return logic.get_action('group_list')(context, data_dict)

def get_resource_download(resource_id):
    return opend_model.get_resource_download(resource_id)

def get_stat_all_view():
    num = opend_model.get_all_view()
    return num

def get_last_update_tracking():
    last_update = opend_model.get_last_update_tracking()
    return last_update

def day_thai(t):
    month = [
        _('January'), _('February'), _('March'), _('April'),
        _('May'), _('June'), _('July'), _('August'),
        _('September'), _('October'), _('November'), _('December')
    ]

    raw = str(t)
    tmp = raw.split(' ')
    dte = tmp[0]

    tmp = dte.split('-')
    m_key = int(tmp[1]) - 1

    if h.lang() == 'th':
        dt = u"{} {} {}".format(int(tmp[2]), month[m_key], int(tmp[0]) + 543)
    else:
        dt = u"{} {}, {}".format(month[m_key], int(tmp[2]), int(tmp[0]))

    return dt

def facet_chart(type, limit):
    items = h.get_facet_items_dict(type, limit)
    i = 1
    data = []
    context = {'model': model}
    for item in items:
        my_dict = {column: value for column, value in item.items()}
        item['rownum'] = i
        if type == 'groups':
            group_dict = logic.get_action('group_show')(context, {'id': item['name']})
            item['image_url'] = group_dict['image_url']
        data.append(item)
        i += 1

    return data

def get_recent_view_for_package(package_id):
    rs = model.TrackingSummary.get_for_package(package_id)
    return rs['recent']

def get_featured_pages(per_page):
    pages = opend_model.get_featured_pages(per_page)
    return pages

def get_page(name):
    #if db.pages_table is None:
    #    db.init_db(model)
    page = opend_model.get_page(name)
    return page

def is_user_sysadmin(user=None):
    """Returns True if authenticated user is sysadmim
    :rtype: boolean
    """
    if user is None:
        user = toolkit.c.userobj
    return user is not None and user.sysadmin


def user_has_admin_access(include_editor_access=False):
    user = toolkit.c.userobj
    # If user is "None" - they are not logged in.
    if user is None:
        return False
    if is_user_sysadmin(user):
        return True

    groups_admin = user.get_groups('organization', 'admin')
    groups_editor = user.get_groups('organization', 'editor') if include_editor_access else []
    groups_list = groups_admin + groups_editor
    organisation_list = [g for g in groups_list if g.type == 'organization']
    return len(organisation_list) > 0

def get_all_groups():
    groups = toolkit.get_action('group_list')(
        data_dict={'include_dataset_count': False, 'all_fields': True})
    pkg_group_ids = set(group['id'] for group
                        in c.pkg_dict.get('groups', []))
    return [[group['id'], group['display_name']]
            for group in groups if
            group['id'] not in pkg_group_ids]

def get_all_groups_all_type(type=None):    
    user_groups = opend_model.get_groups_all_type(type)

    pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
    return [[group['id'], group['display_name']]
                            for group in user_groups if
                            group['id'] not in pkg_group_ids]
