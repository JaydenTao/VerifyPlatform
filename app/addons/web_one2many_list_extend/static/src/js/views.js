/*global openerp, _, $ */

openerp.web_one2many_list_extend = function (instance) {

    instance.web.form.One2ManyListView.include({
        //init: function (parent, dataset, view_id, options) {
        //    this._super(parent, dataset, view_id, _.extend(options || {}, {
        //        GroupsType: instance.web.form.One2ManyGroups,
        //        ListType: instance.web.form.One2ManyList
        //    }));
        //    this.on('edit:after', this, this.proxy('_after_edit'));
        //    this.on('save:before cancel:before', this, this.proxy('_before_unedit'));
        //    this.on('save:after', this, this.proxy("changed_records"));
        //
        //    var self = this;
        //    //add custom event
        //    $(window).off('direct_imported');
        //    $(window).on('direct_imported', function() {
        //        var args = [].slice.call(arguments).slice(1);
        //        //if (args[1].o2m){
        //        self.o2m.view.reload();
        //        //}
        //    });
        //
        //},

        load_list:function(data){
            this._super(data);

            if (this.fields_view.arch.attrs.auto_reload){
                var self = this;
                //add custom event
                $(window).off('direct_imported');
                $(window).on('direct_imported', function() {
                    var args = [].slice.call(arguments).slice(1);
                    //if (args[1].o2m){
                    self.o2m.view.reload();
                    //}
                });

            }
        }
    });

}
