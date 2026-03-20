/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

class EOSDashboardAction extends Component {
    static template = "mi90_eos.Dashboard";
}

class EOSScorecardAction extends Component {
    static template = "mi90_eos.Scorecard";
}

class EOSRocksAction extends Component {
    static template = "mi90_eos.Rocks";
}

class EOSTodosAction extends Component {
    static template = "mi90_eos.Todos";
}

class EOSIssuesAction extends Component {
    static template = "mi90_eos.Issues";
}

class EOSMeetingsAction extends Component {
    static template = "mi90_eos.Meetings";
}

// Registrar las acciones
registry.category("actions").add("mi90_eos.dashboard_action", EOSDashboardAction);
registry.category("actions").add("mi90_eos.scorecard_action", EOSScorecardAction);
registry.category("actions").add("mi90_eos.rocks_action", EOSRocksAction);
registry.category("actions").add("mi90_eos.todos_action", EOSTodosAction);
registry.category("actions").add("mi90_eos.issues_action", EOSIssuesAction);
registry.category("actions").add("mi90_eos.meetings_action", EOSMeetingsAction);
