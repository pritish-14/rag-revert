openerp.hr_employee_tree = function(session){
    var _t = session.web._t,
       _lt = session.web._lt;
    var QWeb = session.web.qweb;
    session.emp = {};
    session.emp.Chart = session.web.Widget.extend({
        template: 'emp.chart',
        init : function(parent,action){
            this._super(parent,action);
            this.ActionManager = parent;
            this.svgGroup;
            this.tree;
            this.root;
            this.zoomListener;
            this.draggingNode = null;
            this.viewerHeight;
            this.viewerWidth;
            this.maxLabelLength = 0;
            this.ds_employee = new session.web.DataSetSearch(this,'hr.employee');
            this.mail_group = new session.web.DataSetSearch(this, 'mail.group');
            this.groups = [];
            this.ds_users = new session.web.DataSetSearch(this, 'res.users');
            this.action = _.clone(action);
            this.domain = this.action.params.domain || this.action.domain || [];
            this.context = _.extend(this.action.params.context || {}, this.action.context || {});
            this.defaults = {};
            
            for (var key in this.action.context.params) {
                if (_.indexOf(['model', 'res_id'], key) == -1) {
                    continue;
                }
                this.context['search_default_' + key] = this.action.context.params[key];
            }
            for (var key in this.context) {
                if (key.match(/^search_default_/)) {
                    this.defaults[key.replace(/^search_default_/, '')] = this.context[key];
                }
            }
            
        },
        start : function(){
            this._super.apply(this);
            var searchview_loaded = this.load_searchview(this.defaults);
            if (! this.searchview.has_defaults) {
                this.search_employee();
            }
        },
        main_tree: function(data){
            var self = this;
            var datas = data[0]
            var dataMap = datas.reduce(function(map, node) {
                map[node.id] = node;
                return map;
            }, {});

            var emp_tree = [];
            datas.forEach(function(node) {
                node['model'] = "hr.employee";
                node.job_id = node.job_id[1];
                node.department_id = node.department_id[1];
                if(node.image){ 
                node.image = 'data:image/*;base64,'+node.image
                } else {
                node.image = ''
                }
                var parent = dataMap[node.parent_id[0]];
                if (parent) {
                    (parent.children || (parent.children = []))
                        .push(node);
                } else {
                    emp_tree.push(node);
                }
            });
            var comp = {}
            comp = data[1];
            comp['children'] = emp_tree;
            self.render_tree(comp);
        },
        render_tree: function(employee_datas) {
            var totalNodes = 0;
            var maxLabelLength = 0;
            var selectedNode = null;
            var panSpeed = 200;
            this.panBoundary = 20;
            var i = 0;
            this.duration = 750;
            var root;
            this.viewerWidth = '100%'
            this.viewerHeight = '100%'
            var tree = d3.layout.tree()
                .size([ this.viewerWidth, this.viewerHeight]);
            this.tree = tree;
            this.diagonal = d3.svg.diagonal()
                .projection(function(d) {
                    return [d.x, d.y];
                });
            this.visit(employee_datas, function(d) {
                totalNodes++;
                this.maxLabelLength = Math.max(d.name.length, maxLabelLength);
            }, function(d) {
                return d.children && d.children.length > 0 ? d.children : null;
            });
            var self = this;
            this.sortTree();
            this.zoomListener = d3.behavior.zoom().scaleExtent([0.1, 2]).on("zoom", function() {self.zoom(svgGroup)});
            $('svg').remove();
            var baseSvg = d3.select("#tree-container").append("svg")
                .attr("width", this.viewerWidth)
                .attr("height", this.viewerHeight)
                .attr("class", "overlay")
                .call(this.zoomListener);
            this.dragListener = d3.behavior.drag()
                .on("dragstart", function(d) {
                    if (d == root) {
                        return;
                    }
                    dragStarted = true;
                    nodes = tree.nodes(d);
                    d3.event.sourceEvent.stopPropagation();
                })
                .on("drag",function(d){
                    if (d == root) {
                        return;
                    }
                    if (self.dragStarted) {
                        domNode = this;
                        this.initiateDrag(d, domNode,tree);
                    }
                    relCoords = d3.mouse($('svg').get(0));
                    if (relCoords[0] < this.panBoundary) {
                        panTimer = true;
                        this.pan(this, 'left');
                    } else if (relCoords[0] > ($('svg').width() - this.panBoundary)) {

                        panTimer = true;
                        this.pan(this, 'right');
                    } else if (relCoords[1] < this.panBoundary) {
                        panTimer = true;
                        this.pan(this, 'up');
                    } else if (relCoords[1] > ($('svg').height() - this.panBoundary)) {
                        panTimer = true;
                        this.pan(this, 'down');
                    } else {
                        try {
                            clearTimeout(panTimer);
                        } catch (e) {

                        }
                    }
                    d.x0 += d3.event.dy;
                    d.y0 += d3.event.dx;
                    var node = d3.select(this);
                    node.attr("transform", "translate(" + d.y0 + "," + d.x0 + ")");
                    self.updateTempConnector();
                })
                .on("dragend", function(d) {
                    if (d == root) {
                        return;
                    }
                    domNode = this;
                    if (selectedNode) {
                        var index = this.draggingNode.parent.children.indexOf(this.draggingNode);
                        if (index > -1) {
                            this.draggingNode.parent.children.splice(index, 1);
                        }
                        if (typeof selectedNode.children !== 'undefined' || typeof selectedNode._children !== 'undefined') {
                            if (typeof selectedNode.children !== 'undefined') {
                                selectedNode.children.push(this.draggingNode);
                            } else {
                                selectedNode._children.push(this.draggingNode);
                            }
                        } else {
                            selectedNode.children = [];
                            selectedNode.children.push(this.draggingNode);
                        }
                        self.expand(selectedNode);
                        self.sortTree();
                        self.endDrag(domNode,tree);
                    } else {
                        self.endDrag(domNode,tree);
                    }
                })
            var svgGroup = baseSvg.append("g");
            this.svgGroup = svgGroup;
            root = employee_datas;
            root.x0 = $("svg").height() / 2;
            root.y0 = 0;
            this.root = root;
            this.update(self.root);
            this.centerNode(root);
        },
        load_searchview: function (defaults) {
            var self = this;
            this.searchview = new session.web.SearchView(this, this.ds_employee, false, defaults || {}, false);
            this.searchview.appendTo(this.$('.oe_view_manager_view_search'))
                .then(function () { self.searchview.on('search_data', self, self.do_searchview_search); });
            if (this.searchview.has_defaults) {
                this.searchview.ready.then(this.searchview.do_search);
            }
            return this.searchview
        },
        do_searchview_search: function (domains, contexts, groupbys) {
            var self = this;
            session.web.pyeval.eval_domains_and_contexts({
                domains: domains || [],
                contexts: contexts || [],
                group_by_seq: groupbys || []
            }).then(function (results) {
                return self.search_employee(results);
            });
        },
        search_employee: function (search) {
            var domain = this.domain.concat(search && search['domain'] ? search['domain'] : []);
            var context = _.extend(this.context, search && search['context'] ? search['context'] : {});
            return this.ds_employee.call('get_employee', [[], domain, context
            ]).then(this.proxy('employee_render'));
        },
        employee_render: function(result) {
            var self = this;
            this.main_tree(result);
        },
        update: function(source) {
                var self = this;
                var levelWidth = [1];
                var childCount = function(level, n) {
                    if (n.children && n.children.length > 0) {
                        if (levelWidth.length <= level + 1) levelWidth.push(0);

                        levelWidth[level + 1] += n.children.length;
                        n.children.forEach(function(d) {
                            childCount(level + 1, d);
                        });
                    }
                };
                childCount(0, this.root);
                var newHeight = d3.max(levelWidth) * 90; 
                this.tree = this.tree.size([newHeight, this.viewerWidth]);
                var nodes = this.tree.nodes(this.root).reverse(),
                    links = this.tree.links(nodes);
                nodes.forEach(function(d) {
                    d.y = (d.depth * (this.maxLabelLength * 30));
                });
                node = this.svgGroup.selectAll("g.node")
                    .data(nodes, function(d) {
                        return d.id || (d.id = ++i);
                    });
                var nodeEnter = node.enter().append("g")
                    .call(this.dragListener)
                    .attr("class", "node")
                    .attr("transform", function(d) {
                        return "translate(" + source.y0 + "," + source.x0 + ")";
                    })
                    
                    .on('click', function(d){self.click(d)})
                 nodeEnter.append("circle")
                    .attr('class', 'nodeCircle')
                    .attr("r", 0)
                    .style("fill", function(d) {
                        return d._children ? "lightsteelblue" : "#fff";
                    });
                    var s=node.append('pattern')
                        .attr('id', function(d){ return d.id })
                        .attr('patternUnits', 'userSpaceOnUse')
                        .attr('x', -31)
                        .attr('y', -34)
                        .attr('width', '95')
                        .attr('height', '110')
                        .append('image')
                        .attr('title',function(d){return d.name;})
                        .attr('xlink:href',function(d){
                            return d.image || 'hr_employee_tree/static/src/img/no-picture.png';
                            })
                        .attr('x', -20)
                        .attr('y', -20)
                        .attr('width', "95")
                        .attr('height', "110");
                nodeEnter.append("text")
                    .attr("x", function(d) {
                        return d.children || d._children ? 0 : 0;
                    })
                    .attr("dy", ".35em")
                    .attr('class', 'nodeText')
                    .attr('title', function(d){return 'Name : '+d.name})
                    .attr("text-anchor", function(d) {
                        return d.children || d._children ? "start" : "start";
                    })
                    .text(function(d) {
                        var nam=d.name.substr(0,7);
                        if(nam.length >= 7) {return nam+'..';}
                        else{return nam;}
                    })
                    .style("fill-opacity", 0);
                nodeEnter.append("circle")
                    .attr('class', 'ghostCircle')
                    .attr("r", 30)
                    .attr("opacity", 0.2) 
                    .style("fill", "red")
                    .attr('pointer-events', 'mouseover')
                    .on("mouseover", function(node) {
                        this.overCircle(node);
                    })
                    .on("mouseout", function(node) {
                        this.outCircle(node);
                    });
                node.select('text')
                    .attr("y", function(d) {
                        return d.children || d._children ? -45 : -45;
                    })
                    .attr("text-anchor", function(d) {
                        return d.children || d._children ? "middle" : "middle";
                    })
                    .text(function(d) {
                        var nam=d.name.substr(0,7);
                        if(nam.length >= 7) {return nam+'..';}
                        else{return nam;}
                    });
                node.select("circle.nodeCircle")
                    .attr("r", 33.5)
                    .style("fill",function(d){
                        d3.select(this)
                            return 'url("#'+d.id+'")';    
                    })
                var nodeUpdate = node.transition()
                    .duration(this.duration)
                    .attr("transform", function(d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    });
                nodeUpdate.select("text")
                    .style("fill-opacity", 1);
                var nodeExit = node.exit().transition()
                    .duration(this.duration)
                    .attr("transform", function(d) {
                        return "translate(" + source.y + "," + source.x + ")";
                    })
                    .remove();
                nodeExit.select("circle")
                    .attr("r", 0);
                nodeExit.select("text")
                    .style("fill-opacity", 0);
                var link = this.svgGroup.selectAll("path.link")
                    .data(links, function(d) {
                        return d.target.id;
                    });
                link.enter().insert("path", "g")
                    .attr("class", "link")
                    .attr("d", function(d) {
                        var o = {
                            x: source.x0,
                            y: source.y0
                        };
                        return self.diagonal({
                            source: o,
                            target: o
                        });
                    });
                link.transition()
                    .duration(this.duration)
                    .attr("d", self.diagonal);
                link.exit().transition()
                    .duration(this.duration)
                    .attr("d", function(d) {
                        var o = {
                            x: source.x,
                            y: source.y
                        };
                        return self.diagonal({
                            source: o,
                            target: o
                        });
                    })
                    .remove();
                nodes.forEach(function(d) {
                    d.x0 = d.y;
                    d.y0 = d.x;
                });
            },
            outCircle: function(d) {
                selectedNode = null;
                this.updateTempConnector();
            },
            overCircle: function(d) {
                selectedNode = d;
                this.updateTempConnector();
            },
            click: function(d) {
                var self = this;
                var attch;
                var emp_id;
                if(d.model != 'res.company'){
                    emp_id = d.id;
                }
                else{emp_id = d.id.split("_")[1];}
                attch = { 
                    'name':d.name,
                    'post':d.job_id +', '+d.department_id,
                    'image':d.image || 'hr_employee_tree/static/src/img/no-picture.png',
                    'href':'#model='+d.model+'&id='+emp_id,
                    }; 
                this.$("#emp-information").html(session.web.qweb.render('hr.employee.profile.data',{'profile':attch}));
                this.$el.find(".oe_employee_action")
                    .off("click").on("click", function(e) {
                    self.open_record(parseInt(emp_id), d.model)
                });
                this.display_buttons(d.message_is_follower);
                this.$el.find(".oe_follower").on('click', function(event) {
                    if($(this).hasClass('oe_notfollow'))
                        self.do_follow(emp_id);
                    else
                        self.do_unfollow(emp_id);
                });
                if (d3.event.defaultPrevented) return;
                d = this.toggleChildren(d);
                this.centerNode(d);
                this.update(d);

                //this.get_mail_wall(parseInt(d.id), d.model);

                this.ds_employee.call('get_recent_activities',[emp_id])
                    .then(function(actvities_data){
                    
                        self.$('.recent_log').html
                        (session.web.qweb.render('hr.employee.recent_activities',{'recentdata':actvities_data}));
                        self.$el.find(".oe_msg_action").off("click").on("click",function(e){
                            self.open_partner(parseInt(5),'res.partner')});
                    });
            },
            /*get_mail_wall: function(id, model) {
                var self = this;
                return new session.web.Model("ir.model.data").call("get_object_reference", ["mail", "action_mail_inbox_feeds"]).then(function(result) {
                    var additional_context = _.extend({
                        active_id: id,
                        active_ids: [id],
                        active_model: model
                    });
                    console.log("additional_context  : ",additional_context);
                    return self.rpc("/web/action/load", {
                        action_id: result[1],
                        context: additional_context
                    }).done(function (result) {
                        result.context = session.web.pyeval.eval('contexts', [result.context, additional_context]);
                        result.flags = result.flags || {};
                        $(".oe_mail_wall").remove();
                        var wall = new session.mail.Wall(self, result);
                        wall.appendTo(".mail_wall_message");
                    });
                });
            },*/
            open_partner: function(id, model) {
                var self = this;
                console.log("This : ",id,model);
                new session.web.Model("ir.model.data").call("get_object_reference", ["base", "open_view_partner_list"]).then(function(result) {
                    var additional_context = _.extend({
                        active_id: id,
                        active_ids: [id],
                        active_model: model
                    });
                    return self.rpc("/web/action/load", {
                        action_id: result[1],
                        context: additional_context
                    }).done(function (result) {
                        result.context = session.web.pyeval.eval('contexts', [result.context, additional_context]);
                        result.flags = result.flags || {};
                        result.flags.new_window = true;
                        result.res_id = id;
                        return self.do_action(result, {
                            on_close: function () {
                                self.do_search(self.last_domain, self.last_context, self.last_group_by);
                            }
                        });
                    });
                });
            },
            open_record: function(id, model) {
                var self = this;
                new session.web.Model("ir.model.data").call("get_object_reference", ["hr", "open_view_employee_list"]).then(function(result) {
                    var additional_context = _.extend({
                        active_id: id,
                        active_ids: [id],
                        active_model: model
                    });
                    return self.rpc("/web/action/load", {
                        action_id: result[1],
                        context: additional_context
                    }).done(function (result) {
                        result.context = session.web.pyeval.eval('contexts', [result.context, additional_context]);
                        result.flags = result.flags || {};
                        result.flags.new_window = true;
                        result.res_id = id;
                        return self.do_action(result, {
                            on_close: function () {
                                self.do_search(self.last_domain, self.last_context, self.last_group_by);
                            }
                        });
                    });
                });
            },
            do_follow: function (node) {
                var self =this;
                this.ds_employee.call('do_follow', [[node], [this.session.uid],'undefine',{}])
                    .then(function() {
                        node.message_is_follower = true;
                        self.read_value(node)
                    });
            },        
            do_unfollow: function (node) {
                var self = this;
                if (confirm(_t("Warning! \nYou won't be notified of any email or discussion on this document. Do you really want to unfollow this document ?"))) {
                var follower_ids = [this.session.uid];
                return this.ds_employee.call('do_unfollow', [[node], follower_ids, {}])
                    .then(function() {
                        node.message_is_follower = false;
                        self.read_value(node)
                    });
                }
            },
            display_buttons: function(message_is_follower) {
                if (message_is_follower) {
                    this.$el.find('button.oe_follower').removeClass('oe_notfollow').addClass('oe_following');
                }
                else {
                    this.$el.find('button.oe_follower').removeClass('oe_following').addClass('oe_notfollow');
                }
            },
            read_value: function (employee_id) {
                var self = this;
                //problem fo read_ids
                return this.ds_employee.read_ids(employee_id, ['message_is_follower']).then(function (results) {
                    if(results.message_is_follower) {
                        self.display_buttons(true);
                    } else {
                        self.display_buttons(false);
                    }
                });
            },
            updateTempConnector: function(selectedNode) {
                var data = [];
                if (this.draggingNode !== null && selectedNode !== null) {
                    data = [{
                        source: {
                            x: selectedNode.y0,
                            y: selectedNode.x0
                        },
                        target: {
                            x: this.draggingNode.y0,
                            y: this.draggingNode.x0
                        }
                    }];
                }
                var link = this.svgGroup.selectAll(".templink").data(data);
                link.enter().append("path")
                    .attr("class", "templink")
                    .attr("d", d3.svg.diagonal())
                    .attr('pointer-events', 'none');
                link.attr("d", d3.svg.diagonal());
                link.exit().remove();
            },
        zoom: function(svgGroup) {
                svgGroup.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
            },
        expand: function(d) {
                if (d._children) {
                    d.children = d._children;
                    d.children.forEach(this.expand);
                    d._children = null;
                }
            },
        centerNode: function(source) {
                var self= this;
                scale = this.zoomListener.scale();
                x = -source.y0;
                y = -source.x0;
                x = x * scale + $('svg').width() / 2;
                y = y * scale + $('svg').height() / 3;
                d3.select('g').transition()
                    .duration(self.duration)
                    .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
                this.zoomListener.scale(scale);
                this.zoomListener.translate([x, y]);
            },
        endDrag: function(domNode) {
                var self= this;
                selectedNode = null;
                d3.selectAll('.ghostCircle').attr('class', 'ghostCircle');
                d3.select(domNode).attr('class', 'node');
                d3.select(domNode).select('.ghostCircle').attr('pointer-events', '');
                self.updateTempConnector();
                if (self.draggingNode !== null) {
                    this.update(this.root);
                    self.centerNode(self.draggingNode);
                    this.draggingNode = null;
                }
            },
        toggleChildren: function(d) {
            var self= this;
            if (d.children) {
                d._children = d.children;
                d.children = null;
                d.y0 = 200;
            } else if (d._children) {
                d.children = d._children;
                d._children = null;
                d.y0 = 450;
            }
            return d;
        },
        initiateDrag: function(d, domNode) {
                var self  = this;
                this.draggingNode = d;
                d3.select(domNode).select('.ghostCircle').attr('pointer-events', 'none');
                d3.selectAll('.ghostCircle').attr('class', 'ghostCircle show');
                d3.select(domNode).attr('class', 'node activeDrag');

                this.svgGroup.selectAll("g.node").sort(function(a, b) { 
                    if (a.id != self.draggingNode.id) return 1;
                    else return -1;
                });
                if (nodes.length > 1) {
                    links = this.tree.links(nodes);
                    nodePaths = this.svgGroup.selectAll("path.link")
                        .data(links, function(d) {
                            return d.target.id;
                        }).remove();
                    nodesExit = this.svgGroup.selectAll("g.node")
                        .data(nodes, function(d) {
                            return d.id;
                        }).filter(function(d, i) {
                            if (d.id == self.draggingNode.id) {
                                return false;
                            }
                            return true;
                        }).remove();
                }
                parentLink = this.tree.links(this.tree.nodes(self.draggingNode.parent));
                this.svgGroup.selectAll('path.link').filter(function(d, i) {
                    if (d.target.id == self.draggingNode.id) {
                        return true;
                    }
                    return false;
                }).remove();

                dragStarted = null;
            },
        visit: function(parent, visitFn, childrenFn) {
                if (!parent) return;
                visitFn(parent);
                var children = childrenFn(parent);
                if (children) {
                    var count = children.length;
                    for (var i = 0; i < count; i++) {
                        this.visit(children[i], visitFn, childrenFn);
                    }
                }
        },
        sortTree: function() {
            this.tree.sort(function(a, b) {
                return b.name.toLowerCase() < a.name.toLowerCase() ? 1 : -1;
            });
        },
        pan: function (domNode, direction) {
                var speed = this.panSpeed;
                if (panTimer) {
                    clearTimeout(panTimer);
                    translateCoords = d3.transform(this.svgGroup.attr("transform"));
                    if (direction == 'left' || direction == 'right') {
                        translateX = direction == 'left' ? translateCoords.translate[0] + speed : translateCoords.translate[0] - speed;
                        translateY = translateCoords.translate[1];
                    } else if (direction == 'up' || direction == 'down') {
                        translateX = translateCoords.translate[0];
                        translateY = direction == 'up' ? translateCoords.translate[1] + speed : translateCoords.translate[1] - speed;
                    }
                    scaleX = translateCoords.scale[0];
                    scaleY = translateCoords.scale[1];
                    scale = this.zoomListener.scale();
                    this.svgGroup.transition().attr("transform", "translate(" + translateX + "," + translateY + ")scale(" + scale + ")");
                    d3.select(domNode).select('g.node').attr("transform", "translate(" + translateX + "," + translateY + ")");
                    this.zoomListener.scale(this.zoomListener.scale());
                    this.zoomListener.translate([translateX, translateY]);
                    panTimer = setTimeout(function() {
                        this.pan(domNode, speed, direction);
                    }, 50);
                }
            },
    });
    session.web.client_actions.add('emp.chart','session.emp.Chart');
};
