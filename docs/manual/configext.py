from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.domains.std import GenericObject, StandardDomain
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import clean_astext, make_refnode
from sphinx.util import ws_re
from sphinx import addnodes
from docutils import nodes

class ConfigOption(ObjectDescription):
    indextemplate = l_('configuration option; %s')
    parse_node = None

    def handle_signature(self, sig, signode):
        if self.parse_node:
            name = self.parse_node(self.env, sig, signode)
        else:
            signode.clear()
            signode += addnodes.desc_name(sig, sig)
            # normalize whitespace like XRefRole does
            name = ws_re.sub('', sig)
        return name

    def add_target_and_index(self, name, sig, signode):
        targetname = '%s-%s' % (self.objtype, name)
        signode['ids'].append(targetname)
        self.state.document.note_explicit_target(signode)
        if self.indextemplate:
            colon = self.indextemplate.find(':')
            if colon != -1:
                indextype = self.indextemplate[:colon].strip()
                indexentry = self.indextemplate[colon+1:].strip() % (name,)
            else:
                indextype = 'single'
                indexentry = self.indextemplate % (name,)
            self.indexnode['entries'].append((indextype, indexentry,
                                              targetname, targetname))
        self.env.domaindata['config']['objects'][self.objtype, name] = \
            self.env.docname, targetname


class ConfigSectionXRefRole(XRefRole):
    """
    Cross-referencing role for configuration sections (adds an index entry).
    """

    def result_nodes(self, document, env, node, is_ref):
        if not is_ref:
            return [node], []
        varname = node['reftarget']
        tgtid = 'index-%s' % env.new_serialno('index')
        indexnode = addnodes.index()
        indexnode['entries'] = [
            ('single', varname, tgtid, varname),
            ('single', _('configuration section; %s') % varname, tgtid, varname)
        ]
        targetnode = nodes.target('', '', ids=[tgtid])
        document.note_explicit_target(targetnode)
        return [indexnode, targetnode, node], []

class ConfigSection(ObjectDescription):
    indextemplate = l_('configuration section; %s')
    parse_node = None

    def handle_signature(self, sig, signode):
        if self.parse_node:
            name = self.parse_node(self.env, sig, signode)
        else:
            signode.clear()
            signode += addnodes.desc_name(sig, sig)
            # normalize whitespace like XRefRole does
            name = ws_re.sub('', sig)
        return name

    def add_target_and_index(self, name, sig, signode):
        targetname = '%s-%s' % (self.objtype, name)
        signode['ids'].append(targetname)
        self.state.document.note_explicit_target(signode)
        if self.indextemplate:
            colon = self.indextemplate.find(':')
            if colon != -1:
                indextype = self.indextemplate[:colon].strip()
                indexentry = self.indextemplate[colon+1:].strip() % (name,)
            else:
                indextype = 'single'
                indexentry = self.indextemplate % (name,)
            self.indexnode['entries'].append((indextype, indexentry,
                                              targetname, targetname))
        self.env.domaindata['config']['objects'][self.objtype, name] = \
            self.env.docname, targetname


class ConfigOptionXRefRole(XRefRole):
    """
    Cross-referencing role for configuration options (adds an index entry).
    """

    def result_nodes(self, document, env, node, is_ref):
        if not is_ref:
            return [node], []
        varname = node['reftarget']
        tgtid = 'index-%s' % env.new_serialno('index')
        indexnode = addnodes.index()
        indexnode['entries'] = [
            ('single', varname, tgtid, varname, None),
            ('single', _('configuration option; %s') % varname, tgtid, varname, None)
        ]
        targetnode = nodes.target('', '', ids=[tgtid])
        document.note_explicit_target(targetnode)
        return [indexnode, targetnode, node], []


class ConfigFileDomain(Domain):
    name = 'config'
    label = 'Config'

    object_types = {
            'option':  ObjType(l_('config option'), 'option'),
            'section':  ObjType(l_('config section'), 'section'),
            }
    directives = {
            'option': ConfigOption,
            'section': ConfigSection,
            }
    roles = {
            'option': ConfigOptionXRefRole(),
            'section': ConfigSectionXRefRole(),
            }

    initial_data = {
        'objects': {},      # (type, name) -> docname, labelid
    }

    def clear_doc(self, docname):
        remove = []
        for key, (fn, _) in self.data['objects'].items():
            if fn == docname:
                remove.append(key)
        for key in remove:
            del self.data['objects'][key]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        docname, labelid = self.data['objects'].get((typ, target), ('', ''))
        if not docname:
            return None
        else:
            return make_refnode(builder, fromdocname, docname,
                                labelid, contnode)

    def get_objects(self):
        for (type, name), info in self.data['objects'].items():
            yield (name, name, type, info[0], info[1],
                   self.object_types[type].attrs['searchprio'])

def setup(app):
    app.add_domain(ConfigFileDomain)

