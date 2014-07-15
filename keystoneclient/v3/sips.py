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

import traceback


class Sip(base.Resource):
    """Represents an Identity sip.

    Attributes:
        * id: a uuid that identifies the sip
        * name: sip name
        * description: sip description
        * enabled: boolean to indicate if sip is enabled

    """
    @utils.positional(enforcement=utils.positional.WARN)
    def update(self, name=None, description=None, enabled=None):
        kwargs = {
            'name': name if name is not None else self.name,
            'description': (description
                            if description is not None
                            else self.description),
            'enabled': enabled if enabled is not None else self.enabled,
        }

        try:
            retval = self.manager.update(self.id, **kwargs)
            self = retval
        except Exception:
            retval = None

        return retval


class SipManager(base.CrudManager):
    """Manager class for manipulating Identity sips."""
    resource_class = Sip
    collection_key = 'sips'
    key = 'sip'

    @utils.positional(1, enforcement=utils.positional.WARN)
    def create(self, name, sid, description=None, enabled=True, **kwargs):
        return super(SipManager, self).create(
            sid_id=base.getid(sid),
            name=name,
            description=description,
            enabled=enabled,
            **kwargs)

    @utils.positional(enforcement=utils.positional.WARN)
    def list(self, sid=None, user=None, **kwargs):
        """List sips.

        If sid or user are provided, then filter sips with
        those attributes.

        If ``**kwargs`` are provided, then filter sips with
        attributes matching ``**kwargs``.
        """
   	#traceback.print_stack()
        base_url = '/users/%s' % base.getid(user) if user else None
        return super(SipManager, self).list(
            base_url=base_url,
            sid_id=base.getid(sid),
            **kwargs)

    def get(self, sip):
        return super(SipManager, self).get(
            sip_id=base.getid(sip))

    @utils.positional(enforcement=utils.positional.WARN)
    def update(self, sip, name=None, sid=None, description=None,
               enabled=None, **kwargs):
        return super(SipManager, self).update(
            sip_id=base.getid(sip),
            sid_id=base.getid(sid),
            name=name,
            description=description,
            enabled=enabled,
            **kwargs)

    def delete(self, sip):
        return super(SipManager, self).delete(
            sip_id=base.getid(sip))
