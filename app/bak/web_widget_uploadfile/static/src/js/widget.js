openerp.web_widget_uploadfile = function (instance) {

    instance.web.form.uploadfile = instance.web.form.FieldBinary.extend({
    template: 'FieldUploadfile',
    initialize_content: function() {
        this._super();
        if (this.get("effective_readonly")) {
            var self = this;
            this.$el.find('a').click(function(ev) {
                if (self.get('value')) {
                    self.on_save_as(ev);
                }
                return false;
            });
        }
    },
    render_value: function() {
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
    on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
        this.binary_value = true;
        this.set_filename(name);
        this.internal_set_value(file_base64);
        var show_value = name + " (" + instance.web.human_size(size) + ")";
        this.$el.find('input').eq(0).val(show_value);
    },
    on_clear: function() {
        this._super.apply(this, arguments);
        this.$el.find('input').eq(0).val('');
        this.set_filename('');
    },
    set_value: function(value_){
        var changed = value_ !== this.get_value();
        this._super.apply(this, arguments);
        // Trigger value change if size is the same
        if (!changed){
            this.trigger("change:value", this, {
                oldValue: value_,
                newValue: value_
            });
        }
    }
});

    instance.web.form.widgets.add('uploadfile', 'instance.web.form.uploadfile');
};
