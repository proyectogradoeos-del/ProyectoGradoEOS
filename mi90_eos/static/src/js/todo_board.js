/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class TodoBoardAction extends Component {
    static template = "mi90_eos.TodoBoardTemplate";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            todos: [],
            loading: false,
        });

        onMounted(async () => {
            await this.loadTodos();
            // attach DOM listeners for static controls (add button / input)
            this.attachDomListeners();
            // enable drag & drop to move todos across columns
            this.enableDragDrop();
        });
    }

    async loadTodos() {
        this.state.loading = true;
        try {
            const todos = await this.rpc("/web/dataset/call_kw", {
                model: "eos.todo",
                method: "search_read",
                args: [[]],
                kwargs: {
                    fields: ["id", "name", "description", "owner_id", "due_date", "status", "progress", "rock_id"],
                    order: "date_create desc",
                },
            });
            this.state.todos = todos;
            this.updateCounts();
        } catch (error) {
            console.error("Error loading todos:", error);
            this.notification.add("Error al cargar las tareas", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    updateCounts() {
        const counts = {
            todo: 0,
            in_progress: 0,
            in_review: 0,
            done: 0,
        };

        this.state.todos.forEach(todo => {
            if (counts.hasOwnProperty(todo.status)) {
                counts[todo.status]++;
            }
        });

        // Update count badges
        Object.keys(counts).forEach(status => {
            const badge = this.el?.querySelector(`.mi90-todos-count-${status}`);
            if (badge) {
                badge.textContent = counts[status];
            }
        });

        this.renderTodos();
    }

    renderTodos() {
        const columns = ['todo', 'in_progress', 'in_review', 'done'];
        
        columns.forEach(status => {
            const column = this.el?.querySelector(`[data-state="${status}"] .todos-column-list`);
            if (column) {
                column.innerHTML = '';
                
                const todosForStatus = this.state.todos.filter(todo => todo.status === status);
                todosForStatus.forEach(todo => {
                    const todoElement = this.createTodoElement(todo);
                    column.appendChild(todoElement);
                });
            }
        });
    }

    createTodoElement(todo) {
        const div = document.createElement('div');
        div.className = 'todo-item';
        div.setAttribute('draggable', 'true');
        div.dataset.id = String(todo.id);
        div.style.cssText = `
            background: white;
            border: 1px solid #e6e6e6;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        `;

        const ownerName = todo.owner_id ? todo.owner_id[1] : 'Sin asignar';
        const dueDate = todo.due_date ? new Date(todo.due_date).toLocaleDateString('es-ES') : 'Sin fecha';
        const statusColor = this.getStatusColor(todo.status);

        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div style="font-weight: 600; color: #2c3e50; flex: 1;">${todo.name}</div>
                <div style="background: ${statusColor}; color: white; padding: 2px 6px; border-radius: 12px; font-size: 10px; font-weight: 600;">
                    ${this.getStatusText(todo.status)}
                </div>
            </div>
            <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
                <i class="fa fa-user" style="margin-right: 4px;"></i>${ownerName}
            </div>
            <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                <i class="fa fa-calendar" style="margin-right: 4px;"></i>${dueDate}
            </div>
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 11px; color: #666;">Progreso</span>
                    <span style="font-size: 11px; font-weight: 600; color: #2c3e50;">${todo.progress}%</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 6px; overflow: hidden;">
                    <div style="background: ${statusColor}; height: 100%; width: ${todo.progress}%; transition: width 0.3s;"></div>
                </div>
            </div>
            <div style="display: flex; gap: 4px;">
                <button class="btn-edit" data-id="${todo.id}" style="background: #007bff; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; flex: 1;">
                    <i class="fa fa-edit"></i> Editar
                </button>
                <button class="btn-delete" data-id="${todo.id}" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px;">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
        `;

        // Add hover effect
        div.addEventListener('mouseenter', () => {
            div.style.transform = 'translateY(-2px)';
            div.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });

        div.addEventListener('mouseleave', () => {
            div.style.transform = 'translateY(0)';
            div.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        });

        // Add event listeners for buttons
        const editBtn = div.querySelector('.btn-edit');
        const deleteBtn = div.querySelector('.btn-delete');

        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.editTodo(todo.id);
        });

        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteTodo(todo.id);
        });

        // Add click to edit on the whole card
        div.addEventListener('click', () => {
            this.editTodo(todo.id);
        });

        // Drag events
        div.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', String(todo.id));
            setTimeout(() => {
                div.style.opacity = '0.5';
            }, 0);
        });
        div.addEventListener('dragend', () => {
            div.style.opacity = '1';
        });

        return div;
    }

    getStatusColor(status) {
        const colors = {
            'todo': '#6c757d',
            'in_progress': '#007bff',
            'in_review': '#ffc107',
            'done': '#28a745',
            'cancel': '#dc3545'
        };
        return colors[status] || '#6c757d';
    }

    getStatusText(status) {
        const texts = {
            'todo': 'POR HACER',
            'in_progress': 'EN CURSO',
            'in_review': 'EN REVISIÓN',
            'done': 'FINALIZADO',
            'cancel': 'CANCELADO'
        };
        return texts[status] || status.toUpperCase();
    }

    async addTodo() {
        const input = this.el?.querySelector('.mi90-todo-new-input');
        if (!input || !input.value.trim()) {
            this.notification.add("Por favor ingrese un nombre para la tarea", { type: "warning" });
            return;
        }
        try {
            // Create the record and get the id
            const newId = await this.rpc('/web/dataset/call_kw', {
                model: 'eos.todo',
                method: 'create',
                args: [{
                    name: input.value.trim(),
                    status: 'todo',
                }],
                kwargs: {},
            });

            input.value = '';
            // Fetch the created record to get all fields
            const records = await this.rpc('/web/dataset/call_kw', {
                model: 'eos.todo',
                method: 'search_read',
                args: [[['id', '=', newId]]],
                kwargs: { fields: ["id", "name", "description", "owner_id", "due_date", "status", "progress", "rock_id"] },
            });
            if (records && records[0]) {
                // Prepend the new todo to state and update counts/UI
                this.state.todos.unshift(records[0]);
                this.updateCounts();
            } else {
                // Fallback: reload all
                await this.loadTodos();
            }
            this.notification.add("Tarea creada exitosamente", { type: "success" });
        } catch (error) {
            console.error("Error creating todo:", error);
            this.notification.add("Error al crear la tarea", { type: "danger" });
        }
    }

    async editTodo(todoId) {
        try {
            // Open the form view for editing
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'eos.todo',
                res_id: todoId,
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {},
            });
            
            // Reload todos after a delay to catch changes
            setTimeout(() => {
                this.loadTodos();
            }, 1000);
        } catch (error) {
            console.error("Error opening edit form:", error);
            this.notification.add("Error al abrir el formulario de edición", { type: "danger" });
        }
    }

    async deleteTodo(todoId) {
        if (!confirm('¿Está seguro de que desea eliminar esta tarea?')) {
            return;
        }

        try {
            await this.rpc("/web/dataset/call_kw", {
                model: "eos.todo",
                method: "unlink",
                args: [[todoId]],
                kwargs: {},
            });

            // Remove from local state to update UI immediately
            const idx = this.state.todos.findIndex(t => t.id === todoId);
            if (idx !== -1) {
                this.state.todos.splice(idx, 1);
            }
            this.updateCounts();
            this.notification.add("Tarea eliminada exitosamente", { type: "success" });
        } catch (error) {
            console.error("Error deleting todo:", error);
            this.notification.add("Error al eliminar la tarea", { type: "danger" });
        }
    }

    attachDomListeners() {
        // Add event listener for the add button
        const addBtn = this.el?.querySelector('.mi90-todo-add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addTodo());
        }

        // Add event listener for Enter key on input
        const input = this.el?.querySelector('.mi90-todo-new-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addTodo();
                }
            });
        }
    }

    enableDragDrop() {
        const columns = this.el?.querySelectorAll('.todos-column');
        if (!columns) return;

        columns.forEach((col) => {
            const list = col.querySelector('.todos-column-list');
            if (!list) return;

            list.addEventListener('dragover', (e) => {
                e.preventDefault();
                list.style.background = '#f1f5f9';
            });
            list.addEventListener('dragleave', () => {
                list.style.background = '';
            });
            list.addEventListener('drop', async (e) => {
                e.preventDefault();
                list.style.background = '';
                const idStr = e.dataTransfer.getData('text/plain');
                const todoId = parseInt(idStr, 10);
                const newStatus = col.getAttribute('data-state');
                if (!todoId || !newStatus) return;

                try {
                    await this.rpc('/web/dataset/call_kw', {
                        model: 'eos.todo',
                        method: 'write',
                        args: [[todoId], { status: newStatus }],
                        kwargs: {},
                    });
                    // update local state
                    const t = this.state.todos.find(t => t.id === todoId);
                    if (t) {
                        t.status = newStatus;
                        // Optionally adjust progress locally:
                        t.progress = this.estimateProgressFromStatus(newStatus);
                    }
                    this.updateCounts();
                } catch (error) {
                    console.error('Error updating status:', error);
                    this.notification.add('No se pudo mover la tarea', { type: 'danger' });
                }
            });
        });
    }

    estimateProgressFromStatus(status) {
        switch (status) {
            case 'done': return 100;
            case 'in_review': return 75;
            case 'in_progress': return 40;
            case 'cancel': return 0;
            default: return 0;
        }
    }
}

registry.category("actions").add("mi90_eos.todo_board", TodoBoardAction);