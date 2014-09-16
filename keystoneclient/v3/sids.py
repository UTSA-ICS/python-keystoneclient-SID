# Copyright 2011 OpenStack Foundation
# Copyright 2011 Nebula, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import traceback

from keystoneclient import base
from keystoneclient import utils


class Sid(base.Resource):
    """Represents an Identity sid.

    Attributes:
        * id: a uuid that identifies the sid
        * name: sid name
        * description: sid description
        * enabled: boolean to indicate if sid is enabled

    """
#    @utils.positional(enforcement=utils.positional.WARN)
#    def update(self, name=None, description=None, enabled=None):
#        kwargs = {
#            'name': name if name is not None else self.name,
#            'description': (description
#                            if description is not None
#                            else self.description),
#            'enabled': enabled if enabled is not None else self.enabled,
#        }
#
#        try:
#            retval = self.manager.update(self.id, **kwargs)
#            self = retval
#        except Exception:
#            retval = None
#
#        return retval
    pass


class SidManager(base.CrudManager):
    """Manager class for manipulating Identity sids."""
    resource_class = Sid
    collection_key = 'sids'
    key = 'sid'

    @utils.positional(1, enforcement=utils.positional.WARN)
    def create(self, name, members, description=None, enabled=True, **kwargs):
	#print("keystone client: members=", members)
        return super(SidManager, self).create(
            name=name,
            members=members,
            description=description,
            enabled=enabled,
            **kwargs)

    @utils.positional(enforcement=utils.positional.WARN)
    def list(self, domain=None, user=None, **kwargs):
	#traceback.print_stack()
        """List sids.

        If domain or user are provided, then filter sids with
        those attributes.

        If ``**kwargs`` are provided, then filter sids with
        attributes matching ``**kwargs``.
        """
        base_url = '/users/%s' % base.getid(user) if user else None
        return super(SidManager, self).list(
            base_url=base_url,
            domain_id=base.getid(domain),
            **kwargs)

    def get(self, sidinfo):
        return super(SidManager, self).get(
            sid_id=base.getid(sidinfo))

    @utils.positional(enforcement=utils.positional.WARN)
    def update(self, sid, name=None, domain=None, description=None,
               enabled=None, **kwargs):
        return super(SidManager, self).update(
            sid_id=base.getid(sid),
            domain_id=base.getid(domain),
            name=name,
            description=description,
            enabled=enabled,
            **kwargs)

    def delete(self, sidinfo):
        return super(SidManager, self).delete(
            sid_id=base.getid(sidinfo))
