from odoo import http, fields
from odoo.http import request
import json
from datetime import date, timedelta

class Mi90EosController(http.Controller):
    @http.route('/mi90_eos/data/rocks', type='http', auth='user', methods=['GET'], csrf=False)
    def rocks(self, **kw):
        rocks = request.env['eos.rock'].sudo().search_read([], ['id', 'name', 'description', 'owner_id', 'due_date', 'status', 'progress'])
        return request.make_response(json.dumps({'success': True, 'rocks': rocks}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/key_results', type='http', auth='user', methods=['GET'], csrf=False)
    def key_results(self, **kw):
        krs = request.env['eos.key_result'].sudo().search_read([], ['id', 'name', 'rock_id', 'target_value', 'current_value', 'unit', 'weight', 'status'])
        return request.make_response(json.dumps({'success': True, 'key_results': krs}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/todos', type='http', auth='user', methods=['GET'], csrf=False)
    def todos(self, **kw):
        # Provide fields matching the eos.todo model
        todos = request.env['eos.todo'].sudo().search_read([], ['id', 'name', 'description', 'owner_id', 'due_date', 'status', 'progress', 'rock_id'])
        return request.make_response(json.dumps({'success': True, 'todos': todos}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/issues', type='http', auth='user', methods=['GET'], csrf=False)
    def issues(self, **kw):
        items = request.env['eos.issue'].sudo().search_read([], ['id', 'name', 'priority', 'resolved', 'owner_id'])
        return request.make_response(json.dumps({'success': True, 'issues': items}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/meetings', type='http', auth='user', methods=['GET'], csrf=False)
    def meetings(self, **kw):
        items = request.env['eos.meeting'].sudo().search_read([], ['id', 'name', 'date'])
        return request.make_response(json.dumps({'success': True, 'meetings': items}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/scorecard', type='http', auth='user', methods=['GET'], csrf=False)
    def scorecard(self, **kw):
        # Minimal scorecard payload (frontend can compute labels)
        rocks = request.env['eos.rock'].sudo().search([])
        total = len(rocks)
        done = sum(1 for r in rocks if r.progress and r.progress >= 100)
        in_progress = sum(1 for r in rocks if r.progress and 0 < r.progress < 100)
        overdue = sum(1 for r in rocks if r.due_date and r.due_date < fields.Date.context_today(request.env))
        payload = {
            'total': total,
            'done': done,
            'in_progress': in_progress,
            'overdue': overdue,
        }
        return request.make_response(json.dumps({'success': True, 'scorecard': payload}), headers=[('Content-Type', 'application/json')])

    @http.route('/mi90_eos/data/scorecard_table', type='http', auth='user', methods=['GET'], csrf=False)
    def scorecard_table(self, **kw):
        """Return scorecard matrix: weeks and KPI rows (owner, name, target, unit, values per week)."""
        # Determine last N weeks ending today
        N = int(kw.get('weeks', 10))
        today = fields.Date.context_today(request.env)
        # Build weeks as ISO week starts (Monday) ending at the current week
        weeks = []
        # ensure today is a date, not string
        monday = today - timedelta(days=today.weekday())
        dt = monday
        for i in range(N):
            weeks.append(str(dt))
            dt = dt - timedelta(days=7)
        weeks.reverse()  # oldest first

        KPI = request.env['eos.kpi'].sudo()
        VAL = request.env['eos.kpi.value'].sudo()
        kpis = KPI.search_read([], ['id', 'name', 'unit', 'target', 'owner_id'])
        # Preload values for all KPIs in time range
        min_date = weeks[0] if weeks else today
        max_date = weeks[-1] if weeks else today
        values = VAL.search_read([
            ('date', '>=', min_date),
            ('date', '<=', max_date)
        ], ['kpi_id', 'date', 'value'])
        # Index values by (kpi_id, week_label)
        by_key = {}
        for v in values:
            k_id = v['kpi_id'][0] if isinstance(v['kpi_id'], list) else v['kpi_id']
            # normalize to week (Monday) key
            vd = v['date']
            if isinstance(vd, str):
                # convert to date object safely
                y, m, d = vd.split('-')
                vd = date(int(y), int(m), int(d))
            wk = vd - timedelta(days=vd.weekday())
            dkey = str(wk)
            by_key.setdefault((k_id, dkey), []).append(v['value'])

        rows = []
        for k in kpis:
            vals = {}
            for w in weeks:
                arr = by_key.get((k['id'], w))
                if arr:
                    # if multiple entries same week/day pick last
                    vals[w] = arr[-1]
            rows.append({
                'owner': k['owner_id'][1] if k.get('owner_id') else '',
                'name': k['name'],
                'target': k.get('target') or 0.0,
                'unit': k.get('unit') or '',
                'values': vals,
            })

        payload = {
            'weeks': weeks,
            'rows': rows,
            'last_update': str(today),
        }
        return request.make_response(json.dumps({'success': True, 'table': payload}), headers=[('Content-Type', 'application/json')])

    # Key Results CRUD
    @http.route('/mi90_eos/data/key_results/create', type='json', auth='user')
    def create_key_result(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        kr = request.env['eos.key_result'].sudo().create(vals)
        return {'success': True, 'id': kr.id}

    @http.route('/mi90_eos/data/key_results/update', type='json', auth='user')
    def update_key_result(self, **data):
        kr_id = data.get('id')
        if not kr_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        kr = request.env['eos.key_result'].sudo().browse(int(kr_id))
        if not kr.exists():
            return {'success': False, 'error': 'not found'}
        kr.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/key_results/delete', type='json', auth='user')
    def delete_key_result(self, **data):
        kr_id = data.get('id')
        if not kr_id:
            return {'success': False, 'error': 'missing id'}
        kr = request.env['eos.key_result'].sudo().browse(int(kr_id))
        if not kr.exists():
            return {'success': False, 'error': 'not found'}
        kr.unlink()
        return {'success': True}

    # Issues CRUD
    @http.route('/mi90_eos/data/issues/create', type='json', auth='user')
    def create_issue(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        rec = request.env['eos.issue'].sudo().create(vals)
        return {'success': True, 'id': rec.id}

    @http.route('/mi90_eos/data/issues/update', type='json', auth='user')
    def update_issue(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        rec = request.env['eos.issue'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/issues/delete', type='json', auth='user')
    def delete_issue(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        rec = request.env['eos.issue'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.unlink()
        return {'success': True}

    # Meetings CRUD
    @http.route('/mi90_eos/data/meetings/create', type='json', auth='user')
    def create_meeting(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        rec = request.env['eos.meeting'].sudo().create(vals)
        return {'success': True, 'id': rec.id}

    @http.route('/mi90_eos/data/meetings/update', type='json', auth='user')
    def update_meeting(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        rec = request.env['eos.meeting'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/meetings/delete', type='json', auth='user')
    def delete_meeting(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        rec = request.env['eos.meeting'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.unlink()
        return {'success': True}

    # Import skeleton endpoint (to be implemented)
    @http.route('/mi90_eos/data/import_xlsx', type='http', auth='user', methods=['POST'], csrf=False)
    def import_xlsx(self, **kw):
        return request.make_response(json.dumps({'success': False, 'error': 'import not implemented yet'}), headers=[('Content-Type', 'application/json')])

    # KPIs CRUD
    @http.route('/mi90_eos/data/kpis/create', type='json', auth='user')
    def create_kpi(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        rec = request.env['eos.kpi'].sudo().create(vals)
        return {'success': True, 'id': rec.id}

    @http.route('/mi90_eos/data/kpis/update', type='json', auth='user')
    def update_kpi(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        rec = request.env['eos.kpi'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/kpis/delete', type='json', auth='user')
    def delete_kpi(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        rec = request.env['eos.kpi'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.unlink()
        return {'success': True}

    # KPI values CRUD
    @http.route('/mi90_eos/data/kpi_values/create', type='json', auth='user')
    def create_kpi_value(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        rec = request.env['eos.kpi.value'].sudo().create(vals)
        return {'success': True, 'id': rec.id}

    @http.route('/mi90_eos/data/kpi_values/update', type='json', auth='user')
    def update_kpi_value(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        rec = request.env['eos.kpi.value'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/kpi_values/delete', type='json', auth='user')
    def delete_kpi_value(self, **data):
        rec_id = data.get('id')
        if not rec_id:
            return {'success': False, 'error': 'missing id'}
        rec = request.env['eos.kpi.value'].sudo().browse(int(rec_id))
        if not rec.exists():
            return {'success': False, 'error': 'not found'}
        rec.unlink()
        return {'success': True}

    @http.route('/mi90_eos/data/rocks/create', type='json', auth='user')
    def create_rock(self, **data):
        # Expect a JSON object with fields for eos.rock
        vals = {k: v for k, v in data.items() if k != 'id'}
        rock = request.env['eos.rock'].sudo().create(vals)
        return {'success': True, 'id': rock.id}

    @http.route('/mi90_eos/data/rocks/update', type='json', auth='user')
    def update_rock(self, **data):
        rock_id = data.get('id')
        if not rock_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        rock = request.env['eos.rock'].sudo().browse(int(rock_id))
        if not rock.exists():
            return {'success': False, 'error': 'not found'}
        rock.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/rocks/delete', type='json', auth='user')
    def delete_rock(self, **data):
        rock_id = data.get('id')
        if not rock_id:
            return {'success': False, 'error': 'missing id'}
        rock = request.env['eos.rock'].sudo().browse(int(rock_id))
        if not rock.exists():
            return {'success': False, 'error': 'not found'}
        rock.unlink()
        return {'success': True}

    @http.route('/mi90_eos/data/todos/create', type='json', auth='user')
    def create_todo(self, **data):
        vals = {k: v for k, v in data.items() if k != 'id'}
        todo = request.env['eos.todo'].sudo().create(vals)
        return {'success': True, 'id': todo.id}

    @http.route('/mi90_eos/data/todos/update', type='json', auth='user')
    def update_todo(self, **data):
        todo_id = data.get('id')
        if not todo_id:
            return {'success': False, 'error': 'missing id'}
        vals = {k: v for k, v in data.items() if k not in ('id',)}
        todo = request.env['eos.todo'].sudo().browse(int(todo_id))
        if not todo.exists():
            return {'success': False, 'error': 'not found'}
        todo.write(vals)
        return {'success': True}

    @http.route('/mi90_eos/data/todos/delete', type='json', auth='user')
    def delete_todo(self, **data):
        todo_id = data.get('id')
        if not todo_id:
            return {'success': False, 'error': 'missing id'}
        todo = request.env['eos.todo'].sudo().browse(int(todo_id))
        if not todo.exists():
            return {'success': False, 'error': 'not found'}
        todo.unlink()
        return {'success': True}
