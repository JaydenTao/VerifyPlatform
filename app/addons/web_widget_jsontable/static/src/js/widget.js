openerp.web_widget_jsontable = function (instance) {

    var QWeb = instance.web.qweb;
    instance.web.form.jsontable = instance.web.form.FieldBinary.extend({
        render_value: function () {
            var self = this;

            /*one2many tree触犯reload时,后重新执行此方法,所以把以前的清空*/
            this.$el.empty();

            var show_value = (this.get('value') !== null && this.get('value') !== undefined && this.get('value') !== false) ? this.get('value') : '';
            var $table = $(QWeb.render("FieldJSONTable", {widget: this}));
            this.$el.prepend($table);

            if (this.node.attrs.auto_reload){
                $(window).off('direct_imported');
                $(window).on('direct_imported', function() {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.call(self,args[0].result,$table)
                    //self.on_file_uploaded.apply(self, args);
                });
            }


            var opts_columns = $.parseJSON(this.node.attrs.columns);
            var opts_scrollY = this.node.attrs.scrollY || '500px';

            self.table = $table.DataTable({
                data: $.parseJSON(show_value[0]),
                columns: opts_columns,
                scrollY:        opts_scrollY,
                autoWidth: false,
                scrollX: true,
                scrollCollapse: true,
                paging:         false,
                ordering: false,
                info:     false,
                searching: false,
                }
            );

        },

        on_file_uploaded:function(data,$table){
            this.table.clear().draw();
            //this.table.rows.add($.parseJSON(data)).draw();
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

    instance.web.form.widgets.add('jsontable', 'instance.web.form.jsontable');

    //instance.web.DirectImport.uploaded_file=function(){
    //        this.$('.oe_import_button')
    //                .prop('disabled', false);
    //        alert("OK");
    //    }

};
