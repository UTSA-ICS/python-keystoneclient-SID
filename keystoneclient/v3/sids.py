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

from keystoneclient import base
from keystoneclient import utils


class Sid(base.Resource):
    """Represents an Identity sid.

    Attributes:
        * id: a uuid that identifies the sid

    """
    pass


class SidManager(base.CrudManager):
    """Manager class for manipulating Identity sids."""
    resource_class = Sid
    collection_key = 'sids'
    key = 'sid'

    @utils.positional(1, enforcement=utils.positional.WARN)
    def create(self, name, description=None, enabled=True, **kwargs):
        return super(SidManager, self).create(
            name=name,
            description=description,
            enabled=enabled,
            **kwargs)

    def get(self, sid):
        return super(SidManager, self).get(
            sid_id=base.getid(sid))

    def list(self, **kwargs):
        """List sids.

        ``**kwargs`` allows filter criteria to be passed where
         supported by the server.
        """
        # Ref bug #1267530 we have to pass 0 for False to get the expected
        # results on all keystone versions
        if kwargs.get('enabled') is False:
            kwargs['enabled'] = 0
        return super(SidManager, self).list(**kwargs)

    @utils.positional(enforcement=utils.positional.WARN)
    def update(self, sid, name=None,
               description=None, enabled=True, **kwargs):
        return super(SidManager, self).update(
            sid_id=base.getid(sid),
            name=name,
            description=description,
            enabled=enabled,
            **kwargs)

    def delete(self, sid):
        return super(SidManager, self).delete(
            sid_id=base.getid(sid))
