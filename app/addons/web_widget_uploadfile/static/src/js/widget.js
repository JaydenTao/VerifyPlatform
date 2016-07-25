openerp.web_widget_uploadfile = function (instance) {

    instance.web.form.uploadfile = instance.web.form.FieldBinary.extend({
        template: 'FieldUploadfile',
        initialize_content: function () {
            this._super();
            if (this.get("effective_readonly")) {
                var self = this;
                this.$el.find('a').click(function (ev) {
                    if (self.get('value')) {
                        self.on_save_as(ev);
                    }
                    return false;
                });
            }
        },
        render_value: function () {
            var show_value;
            if (!this.get("effective_readonly")) {
                if (this.node.attrs.filename) {
                    show_value = this.view.datarecord[this.node.attrs.filename] || '';
                } else {
                    show_value = (this.get('value') !== null && this.get('value') !== undefined && this.get('value') !== false) ? this.get('value') : '';
                }
                this.$el.find('input').eq(0).val(show_value);
            } else {
                this.$el.find('a').toggle(!!this.get('value'));
                if (this.get('value')) {
                    show_value = _t("Download");
                    if (this.view)
                        show_value += " " + (this.view.datarecord[this.node.attrs.filename] || '');
                    this.$el.find('a').text(show_value);
                }
            }
        },
        on_file_uploaded_and_valid: function (size, name, content_type, file_base64) {
            this.binary_value = true;
            this.set_filename(name);
            this.internal_set_value(file_base64);
            var show_value = name + " (" + instance.web.human_size(size) + ")";
            this.$el.find('input').eq(0).val(show_value);
        },
        on_clear: function () {
            this._super.apply(this, arguments);
            this.$el.find('input').eq(0).val('');
            this.set_filename('');
        },
        set_value: function (value_) {
            var changed = value_ !== this.get_value();
            this._super.apply(this, arguments);
            // Trigger value change if size is the same
            if (!changed) {
                this.trigger("change:value", this, {
                    oldValue: value_,
                    newValue: value_
                });
            }
        }
    });

    instance.web.form.widgets.add('uploadfile', 'instance.web.form.uploadfile');


    "use strict";
    var QWeb = instance.web.qweb;
    instance.web.list.uploadfile = instance.web.list.Column.extend({
        format: function (row_data, options) {
            var self = this;
            var record_id = row_data.id.value;
            /*
             因为在表格中有多个上传框,需要通过ID来标识.
             后继的处理,可以参考view_form.js中的上传附件了.
             * */
            self.fileupload_id = "oe_fileupload" + record_id;
            self.form_id = "oe_form_file" + record_id;
            self.input_file_id = "input_file" + record_id;
            self.input_v_file_id ="input_v_file" + record_id;
            self.btn_upload_id = "btn_upload" + record_id;

            //button在tree中会激发action,所以fix it.
            self.record_id = record_id;
            self.action = options.action;
            return QWeb.render('FieldUploadfile',
                {widget: self});
        },
    });
    instance.web.list.columns.add('field.uploadfile', 'instance.web.list.uploadfile');

    instance.web.ListView.include({
        handle_button: function (name, id, callback) {
            var action = _.detect(this.columns, function (field) {
                return field.name === name;
            });
            if (!action) {
                action = _.detect(this.columns, function (field) {
                    return field.widget === "uploadfile" && field.state
                });
                if (!action)
                    return;
                action.type = "object";
                action.name = action.action;
            }
            if ('confirm' in action && !window.confirm(action.confirm)) {
                return;
            }

            var c = new instance.web.CompoundContext();
            c.set_eval_context(_.extend({
                active_id: id,
                active_ids: [id],
                active_model: this.dataset.model
            }, this.records.get(id).toContext()));
            if (action.context) {
                c.add(action.context);
            }
            action.context = c;
            this.do_execute_action(
                action, this.dataset, id, _.bind(callback, null, id));
        }
    });
    instance.web.ListView.List.include({
        render_cell: function (record, column) {
            if (column.widget == "uploadfile") {
                var self = this;
                var record_id = record.attributes.id;

                column.state = false;//防止未选文件时点击上传
                column.name = column.id;//防止未选文件时点击上传
                this.$current.undelegate("#input_file" + record_id,'change');
                this.$current.delegate("#input_file" + record_id,'change',function(e){
                    //var file = e.target.files[0];
                    var path = $(e.target).val();
                    self.$current.find("#input_v_file"+record_id).val(path);
                    $('#btn_upload' + record_id).removeAttr('disabled');

                    column.state = true;
                });

                this.$current.undelegate('#btn_upload' + record_id, 'click');
                this.$current.delegate('#btn_upload' + record_id, 'click', function (e) {
                    var file_node = $("#input_file"+record_id)[0];
                    if (file_node.files.length < 1)
                        return
                    $('#oe_form_file'+record_id).submit();
                });

                return column.format(record.toForm().data, {
                    model: this.dataset.model,
                    id: record.get('id'),
                    action: column.action
                });
            }
            return this._super(record, column);

        }
    });

    instance.web.client_actions.add('web_widget_uploadfile.bt_start', 'instance.web_widget_uploadfile.btn_start');

    instance.web_widget_uploadfile.btn_start = function (parent, action) {
        var self = this;
        action.context.active_id;
        alert('test');
        // and do something...
        return false;
    };

};
