/**
 * Created by Leo on 17-1-18.
 */
    /**
    function switch_hosts() {   // 根据下拉框来切换容器显示列表
        var select_host = $('#switch_host').val();
        for(var host_ip in $('.real_host_ip').text().splice){
{#            if(select_host != host_ip){#}
                console.log()

        }//end for
    }}
     **/

    function select_all_containers() {    // 全选，选中所有容器
        $('input:checkbox').prop('checked',true);
    }

    function reverse_all_containers() {   // 反选, 反选所有容器
        $('input:checkbox').each(function () {
            if (!$(this).prop('checked')) {
                $(this).prop('checked', true)
            }else{
                 $(this).prop('checked', false)
            }
        })
    }


    function cancel_all_containers() {   // 取消选择
        $('input:checkbox').prop('checked',false);
    }


    // 把手动刷新的内容加载到显示表格里
    function show_all_containers(arg) {
            $('#exec_status').remove();
            $('.show_line').remove();

            $.each($('#first_tr').children('td'),function () {    // 在执行玩完查看容器的进程信息后，需要把表格标题还原回去
                // 还原到第一步就是先删除原来有到标题，在插入新到标题
                if($(this).index() >3 ){
                    $(this).remove()
                }
            });
            var td_code = "<td>容器镜像</td><td>运行的命令</td><td>创建时间</td><td>运行状态</td><td>数据更新时间</td>";
            $('#first_tr').append(td_code);  // 插入新到标题

            var disconnect_hosts = arg.disconnect_hosts;
            if( disconnect_hosts != undefined ){
                for (var i in disconnect_hosts){
                    var html_code = '<tr class="show_line"><td><input type="checkbox"></td><td>服务器 <span style="color:red">'
                            +disconnect_hosts[i] +' </span>链接不上</td> </tr>';
                    $('#first_tr').after(html_code);
                }
            };
            for (var info in arg) {
                var container_info = arg[info];
                if (info != 'disconnect_hosts'){
                    var html_code = ' <tr class="show_line"><td><input host_port="'+ container_info.Real_host_ip+'" type="checkbox" name="' + container_info.Container_id + '" value="' + container_info.Container_id + '"></td> ' +
                            '<td><a class="real_host_ip" href="/BatchM/DockerM.html/' + container_info.Real_host_ip + '">' + container_info.Real_host_ip + '&nbsp;</a></td> ' +
                            '<td><a href="/BatchM/DockerM.html/' + container_info.Container_id + '"class="container_id">' + container_info.Container_id.substring(0, 12) + '</a></td>' +
                            '<td>' + container_info.Container_name + '</td>' +
                            '<td>' + container_info.Container_image + '</td>' +
                            '<td>' + container_info.Command + '</td> ' +
                            '<td>' + container_info.Created + '</td> ' +
                            '<td>' + container_info.Status + '</td> ' +
                            '<td>' + container_info.Record_time + '</td><tr>';
                    $('#first_tr').after(html_code);
                } // end if
            }
        }


    // 刷新当前容器信息
    function fresh_all_containers() {
        $('#myButton').button('loading');
        // business logic...
        $.ajax({
            url: "{%  url 'all_containers_info' %}",
            type:'post',
            dataType:'json',
            token:csrftoken,
            data:{'refresh':"True",'action':'select',"type":'containers'},
            success:function (callback) {
                show_all_containers(callback);
                $('#myButton').button('reset');
            }, //end success
            error:function (callback) {
                alert('刷新失败  ',callback);
{#                show_all_containers(callback);#}
                $('#myButton').button('reset')
                }
            });
        }

    // 搜索容器的
    function search_container(arg) {
        var action_type = $(arg).val();
        console.log(action_type);
        if (action_type == "搜索容器"){
            var container_name = $('#container_search').val().trim();
            var get_url = '{% url "all_containers_info" %}'

        } else if(action_type == "搜索镜像") {
            var container_name = $('#images_search').val().trim();
            var get_url = '{% url "all_images_info" %}'
        }
        console.log(get_url,container_name);
        $.ajax({
            url: get_url,
            type: 'get',
            dataType:'json',
            token:csrftoken,
            data:{'container_info':container_name},
            success: function (callback) {
                    console.log(callback);
                    if(action_type == "搜索容器"){show_all_containers(callback)}
                    else if(action_type == "搜索镜像"){show_new_images(callback)}

            },//end success
            error:function (callback) {
                alert('查找失败,请确保名字或ID正确  ',callback);
            } //end err
        }); // end ajax
        }


    // 更改模态框内容的
    function show_madel(arg,mode) {
        if (mode == "ALERT"){
            alert(arg)   // 弹出警告，没有选中任何机器
            $('#myModal').modal('toggle');   // 清除模态框
        }else{
            $('#myModal').modal('toggle');
            $('.modal-body').html(arg);
        }
    }


    // 显示对容器操作的执行状态
    function show_exec_status(trid,arg) {
        // console.log('show_exec_status',arg);
        var exec_succ = "<td><span style='background-color:lightgreen'>执行成功</td>";  // 定义文本执行成功到内容
        var exec_err = "<td><span style='background-color:orange'>执行失败</td>";  // 定义文本执行失败到内容
        var space_place = "<td></td>";
        var success_list = arg.success[0];
        console.log(success_list,'success_list');
        $('#exec_status').remove();   // 删除这个状态栏,避免后面重复叠加l
        $('#'+trid).append("<td id='exec_status'>执行状态</td>");  // 每行末尾添加一个显示执行状态到列

        if (trid == 'first_tr'){
             var error_list = arg.error;   // 这里到error列表返回来到事容器ID，容器ID是独一无二的，所以只需要匹配容器ID就可以了。
            $.each($('input:checkbox'),function(){   // 获取所有选中到的input 的标签
                //if($(this).prop('checked') == true){    // 因为点击操作容器按钮后会出现弹框，所有用户没有足够到时间来做反选，全选到动作，
                    // 所以不许要判断全部复选框，只需要判断选中的复选框就行来。
                    for(var i in success_list){
                           // console.log('succes',i);
                            var ci = i.substring(0,12);
                            var container_id = $(this).parent('td').siblings().children('.container_id').text().trim();
                            if(ci == container_id) {
                                $(this).parents('td').parent().append(exec_succ);   //显示这次到执行状态
                            }
                    } // end for

                   for (var i in error_list){
                      // console.log('error',error_list[i]);
                       var ci = error_list[i].substring(0,12);
                       var container_id = $(this).parent('td').siblings().children('.container_id').text().trim();
                        if(ci == container_id) {
                            $(this).parents('td').parent().append(exec_err); //显示这次到执行状态
                        } // end if
                    } // end for
                }); // end each
        }else if(trid == 'second_tr'){    // 需要判断所有到复选框，因为不会出现弹框，所以用户有足够到时间来做全选反选动作。
             var error_list = arg.error[0];    // 后台返回来到数据是宿主机IP和镜像ID，根据宿主机IP和镜像ID同时在html页面匹配后显示执行状态
             $.each($('input:checkbox'),function(){
                 var image_host_id = $(this).attr('host_port') + $(this).val();
                 console.log('image_host_id',image_host_id);
                 for(var err in error_list){
                    console.log('hehe',error_list[err],err);
                     var return_host_id = err+error_list[err];
                     if(image_host_id==return_host_id){
                         /**if($(this).parent().siblings().length > 9){   // 通过标签个数来判断是否添加来状态提醒
                                    $(this).parent().siblings().last().remove();  // 删除上一次到执行状态
                                } **/
                         $(this).parents('td').parent().append(exec_err)

                     }
                 }// end for
                 for (var succ in success_list){
                     console.log('succ',succ,success_list[succ]);
                     var return_host_id = succ+success_list[succ];
                      if(image_host_id==return_host_id){
                         $(this).parents('td').parent().append(exec_succ)
                     }
                 }
             }); // end each
        }}


    // 显示容器内部进程信息的
    function show_container_process(arg) {
        //var success_list = arg.success;
        //var error_list = arg.error;
        // 首先把原来到标题给清空掉
        $.each($('#first_tr').children('td'),function () {
            if ($(this).index() > 3 ){
                $(this).remove()
            }
        });
        var html_code = "<td>用户</td><td>CPU占用率</td><td>内存占用率</td><td>进程状态</td><td>进程启动时间</td><td>执行的命令</td>";
        $('#first_tr').append(html_code);
        console.log(arg);
        var success_list = arg.success[0];   // 提取获取进程信息成功列表
        var error_list = arg.error;   //  获取进程信息失败到列表
        for (var container_processes in success_list){   // 遍历进程信息成功列表
            $.each($('.show_line'),function()  {
                $(this).append('<td></td>');   // 在每一行添加一个td标签
                var input_checkbox = $(this).children('td').children('input:checkbox').val();
                // 进行匹配容器ID，匹配到位后提取该容器信息到值
                if( input_checkbox == container_processes ){
                    var processes = success_list[container_processes].Processes;   // 把进程信息的列表信息提取出来
                    $.each($(this).children('td'),function (){    // 清空当前行的td栏的内容
                        if($(this).index() > 3 ) {
                            $(this).empty()
                        }
                    });
                    for (var i in processes){    // 遍历每一个进程信息
                        var each_process = processes[i];
                        var user = each_process[0];
                        var CPUusage = each_process[2];
                        var MemUsage = each_process[3];
                        var ProStatus = each_process[7];
                        var StartTime = each_process[8];
                        var Command = each_process[10];
                        // 遍历每一行内容的td标签,匹配到index相等到值就把上面这些获取到进程信息塞入进去
                        $.each($(this).children('td'),function () {
                           if($(this).index() == 4){
                                $(this).append(user+',<br>')
                           }else if($(this).index() == 5){
                                $(this).append(CPUusage+',<br>')
                           }else if($(this).index() == 6){
                                $(this).append(MemUsage+',<br>')
                           }else if($(this).index() == 7){
                                $(this).append(ProStatus+',<br>')
                           }else if($(this).index() == 8){
                                $(this).append(StartTime+',<br>')
                           }else if($(this).index() == 9){
                                $(this).append(Command+',<br>')
                           }

                        });// end each
                    }// end for
                } // end if
            }) // end each
        }
        for(var error_container in error_list){
            var err = error_list[error_container];
            $.each($('.show_line'),function()  {   // 遍历tr/td标签，匹配到容器ID后打上标签

                var input_checkbox = $(this).children('td').children('input:checkbox').val();
                // 进行匹配容器ID，匹配到位后提取该容器信息到值
                if( input_checkbox == err ) {
                    $.each($(this).children('td'),function (){    // 清空当前行的td栏的内容
                        if($(this).index() > 3 ) {
                            $(this).empty()
                        }
                    });
                    $.each($(this).children('td'), function () {
                        if ($(this).index() == 4) {
                            $(this).append('<span style="background-color: orange;">容器链接没有运行或者已经死亡' +
                                    ',  检索不到任何进程信息</span>')
                        }// end if
                    });// end each
                }
            })
        }
    }

    // 启动和停止指定的容器
    function start_containers(arg) {
        var container_id_array = {};
        var action_type = $(arg).attr('id');     // 获取操作按钮的类型，通过这个来判断做什么动作
        var cmd = '';   //定义这个变量，避免ajax提交的时候后面出错
        $.each($('.table input:checkbox'),function(){   // 获取所有选中到的input 的标签
            if($(this).prop('checked') == true){
                container_id_array[($(this).val())] = $(this).attr('host_port');  // 做成一个字典,以容器ID为key，宿主机IP为value
            }// end if
        });
        var close_button = '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';  // 在弹下来的模态框做一个close按钮.
        $('.modal-footer').html(close_button);
        var lenarray = len_of_dict(container_id_array);
        console.log('lenarray',lenarray,container_id_array);
        if ( lenarray == 0){   // 判断是否选中来某一个容器
            var return_body= "您没有选中一个容器！！！<br>您没有选中一个容器！！！<br>您没有选中一个容器！！！重要事情说三遍";
            if (action_type == "exec_cmd" ) {
                show_madel(return_body,'ALERT');
            }else{
                show_madel(return_body);
            }
            return false
        }


        if(action_type=="stop_containers"){
            var action = "stop";
            var type = 'containers';
            var button_text = $('#stop_containers').val();
            $('#stop_containers').val('停止选定容器中.....')

        }else if(action_type=="start_containers") {
            var action = "start";
            var type = 'containers'
            var button_text = $('#start_containers').val();
            $('#start_containers').val('启动选定容器中.....')

        }else if (action_type == "remove_containers") {
            var action = "delete";
            var type = 'containers';
            var button_text = $('#remove_containers').val();
            $('#remove_containers').val('删除选定容器中.....')

        }else if(action_type == 'show_process'){
            var action = 'top';
            var type = 'containers';
            var button_text = $('#show_process').val();
            $('#show_process').val('获取进程信息中......')
        }else if(action_type == "exec_cmd"){
            var action = 'exec_cmd';
            var type = "containers";
            var cmd = $('.modal-body #exec_cmd_input').val();     // 获取执行命令
            var button_text = $('#show_exec_cmd_from').val();
            $('#show_exec_cmd_from').val('执行命令中......')

        }// end if

        var id_array = JSON.stringify(container_id_array);   // json化数据
        var default_body = '请勿狂点同一个提交按钮,<br><br>请求已提交后台处理,<br>处理完成后将会在每一行到末尾显示执行状态,&nbsp;请注意查看......';
        show_madel(default_body);

        $.ajax({   // 开始提交数据到后台去启动对应到容器
            url: '{% url 'docker_containers_manage' %}',
            type:'post',
            dataType:'json',
            token:csrftoken,
            data:{'container_id_array':id_array,'action':action,'type':type,'cmd':cmd},
            success:function(callback){
                if (action_type == 'show_process') {
                    show_container_process(callback);
                    $('#' + action_type).val(button_text);  // 把按钮原来的文本内容复位回去。
                }else if(action_type == 'exec_cmd'){
                    $('#show_exec_cmd_from').val(button_text)    // 因为执行命令的按钮ID不一样，所有这里需要单独判断一下
                    show_exec_status('first_tr', callback);   //展示执行状态
                } else {
                    $('#' + action_type).val(button_text); // 把按钮原来的文本内容复位回去。
                    show_exec_status('first_tr', callback);   //展示执行状态

                }
            }, //end success
            error: function(callback){
                console.log(callback)
            } // end error
        }); // end ajax
    }


    // 统计字典长度
    function len_of_dict(arg) {
        a = 0;
        for(var i in arg){
            if( arg[i] == undefined ){
                break
            }else{
                a=a+1
            }
        } // end for
        return a
    }

    // 搜索容器信息后也是通过这个方法来展现的
    function show_new_images(arg) {
            $('#exec_status').remove();
            $('.show_line').remove();
            var disconnect_hosts = arg.disconnect_hosts;
            if( disconnect_hosts != undefined ){
                for (var i in disconnect_hosts){
                    var html_code = '<tr class="show_line"><td><input type="checkbox"></td><td>服务器 <span style="color:red">'
                            +disconnect_hosts[i] +' </span>链接不上</td> </tr>';
                    $('#first_tr').after(html_code);
                }
            }
            for (var info in arg) {
                var image = arg[info];
                if (info != 'disconnect_hosts'){

                    var html_code = ' <tr class="show_line"><td><input host_port="'+ image.host_ip+'" type="checkbox" name="' + image.image_id + '" value="' + image.image_id + '"></td> ' +
                            '<td><a class="host_ip" href="/BatchM/DockerM.html/' + image.host_ip + '">' + image.host_ip + '&nbsp;</a></td> ' +
                            '<td><a href="/BatchM/DockerM.html/' + image.image_id + '"class="image_id">' + image.image_id.substr(0,13) + '</a></td>' +
                            '<td>' + image.Repo_tags + '</td>' +
                            '<td>' + image.Repo_digests + '</td>' +
                            //'<td>' + transformtime(image.Created) + '</td> ' +
                            '<td>' + image.Created + '</td> ' +
                            '<td>' + image.Image_size + '</td> ' +
                            '<td>' + image.Virtual_size + '</td> ' +
                            '<td>' + image.Labels + '</td>'+
                            '<td>' + image.update_time+'</td><tr>';
                    $('#second_tr').after(html_code);
                } // end if
            }
    }

    // 转换时间的，从unix时间到人肉眼可以识别的时间
    function transformtime(arg) {
        var unixtime = new Date(arg*1000);
        var unixtime = unixtime.toLocaleString();
        return unixtime

    }


    // 刷新镜像信息后通过这个方法展现
    function refresh_image_info(arg) {
        var mydate = new Date();
        success_list = arg.success;
        error_list = arg.error;
        $('#exec_status').remove();
        $('.show_line').remove();
        var succ_list = success_list[0];
        for(var image in succ_list){    // 遍历刷新成功的列表
            //console.log(succ_list[image]);
            //console.log(succ_list[image].Labels);
            console.log('image',image);
            console.log('succ_list',succ_list[image]);
            var image_list = succ_list[image]
            for (var per_image in image_list ){
                var html_code = ' <tr class="show_line"><td><input host_port="'+ image+'" type="checkbox" name="' + image_list[per_image].Id + '" value="' + image_list[per_image].Id + '"></td> ' +
                                '<td><a class="host_ip" href="/BatchM/DockerM.html/' + image + '">' + image + '&nbsp;</a></td> ' +
                                '<td><a href="/BatchM/DockerM.html/' + image_list[per_image].Id + '"class="image_id">' + image_list[per_image].Id.substr(0,13) + '</a></td>' +
                                '<td>' + image_list[per_image].RepoTags + '</td>' +
                                '<td>' + image_list[per_image].RepoDigests + '</td>' +
                                '<td>' + transformtime(image_list[per_image].Created) + '</td> ' +
                               // '<td>' + image_list[per_image].Created + '</td> ' +
                                '<td>' + image_list[per_image].Size + '</td> ' +
                                '<td>' + image_list[per_image].VirtualSize + '</td> ' +
                                '<td>' + [(succ_list[image].Labels == undefined) ?  " " :succ_list[image].Labels] + '</td>'+ // 添加上[]来包裹三元运算后前端展示就不会出问题
                                '<td>' + mydate.toLocaleString() +'</td><tr>';
                $('#second_tr').after(html_code);
            }
        }
        for(var err in error_list[0]){     // 遍历刷新失败的列表
           var html_code = '<tr class="show_line"><td><input type="checkbox"></td><td>服务器 <span style="color:red">'
                            +err +' </span>链接不上或者其他原因导致刷新失败，请检查次这台服务器</td> </tr>';
            $('#second_tr').after(html_code);
        }
    }

    //显示镜像,删除镜像，添加镜像的
    function manage_images(arg) {
        var action_type = $(arg).attr('id');
        if (action_type == 'ShowImages') {

            var action = 'select';
            var type = 'images';
            var hosts = 'all';
            var button_text = $('#ShowImages').val();
            $('#ShowImages').val('刷新中.....');

        }else if(action_type == 'delete_images') {

            var container_id_array = {};
            $.each($('.table input:checkbox:checked'),function(){   // 获取所有选中到的input 的标签
                container_id_array[($(this).val())] = $(this).attr('host_port')
            });
            var lenarray = len_of_dict(container_id_array);
            console.log(lenarray);
            if ( lenarray == 0){   // 判断是否选中来某一个容器
                return_body= "您没有选中一个镜像！！！<br>您没有选中一个镜像！！！<br>您没有选中一个镜像！！！重要事情说三遍";
                show_madel(return_body);
                return false
            }else{

                var action = 'delete';
                var type = 'images';
                var hosts = {};
                $.each($('.table input:checkbox:checked'),function () {
                    if(  hosts[$(this).attr('host_port')] ){  // 先判断有没有这个KEY,有的话再在后面追加镜像ID，没有的话，新添加镜像ID。
                         hosts[$(this).attr('host_port')].push($(this).val())
                    }else {
                        hosts[$(this).attr('host_port')] = [$(this).val()]
                    }
                });
                var button_text = $('#delete_images').val();
                $('#delete_images').val('删除中.....');
                hosts = JSON.stringify(hosts);
                console.log('hosts',hosts);
            }

        }else if(action_type == "add_image"){
            var action = 'push';
            var type = 'images';

            var button_text = $('#add_image').val();
            $('#add_image').val('添加中......')
        } // end if

        $.ajax({
            url:'{% url "docker_containers_manage" %}',
            type:'POST',
            dataType: 'json',
            token:csrftoken,
            data: {'action':action,'type':type,'hosts':hosts},
            success:function(callback){
                if(action=='select'){
                    refresh_image_info(callback);
                    $('#ShowImages').val(button_text);
                }else if (action=='delete'){
                    show_exec_status('second_tr',callback);
                    $('#delete_images').val(button_text);
                }else if(action=='push'){
                    show_new_images(callback);
                    $('#add_image').val(button_text)
                }
                $('#show_images').val(button_text)
            }, // end success
            error: function(callback) {
                alert('操作失败，请联系平台管理员!!')
            } // end error
        }); // end ajax
    }

    // 显示创建容器的更高级创建参数,使用delegate这种方式来绑定按钮的事件，是因为模态框里的内容是后来填充进去的，
    // 导致之前定义的onlick事件无法生效，所以采用这种方式绑定事件
    $('#myModal').delegate('#showMoreConfig', 'click', function () {
        if($(this).prop('checked')) {
            $('#myModal').find('#complex_config').show();
        } else {
            $('#myModal').find('#complex_config').hide();
        }
    });

    // 载创建容器信息的时候，显示模态框的内容
    function show_create_table() {
        var create_table = $('#create_container_div').html();
        var create_button = $('#create_container_button').html();
        $('#myModal').modal('toggle');
        $('.modal-body').html(create_table);
        $('.modal-footer').html(create_button);
    }


    // 获取填写创建容器信息的表格，然后提交到后台处理。
    // 使用$('#myModal').find()来查找内容，因为这个模态框里的内容是后来填充进去的，这样才能找到值。
    function create_container(arg) {
        var container_name =  $('#myModal').find('#name').val().trim();
        var create_info = {};
        if(container_name.length > 0 ){
            $.each($('#myModal').find('#create_container_form select'),function () {   // 遍历select标签，获取用户所选到的值
                create_info[$(this).attr('id')] =  $(this).val()
            });
           $.each($('#myModal').find('#create_container_form input:text'),function () {   // 遍历input是text类型的标签，获取用户所选到的值
               if($(this).attr('id').startsWith('cpu')){
                   create_info[$(this).attr('id')] = Number($(this).val())
               }else {
                   create_info[$(this).attr('id')] = $(this).val();
               }
           });
           $.each($('#myModal').find('#create_container_form input:radio:checked'),function () {   // 遍历input是radio类型的标签，获取用户所选到的值
               create_info[$(this).attr('id')] = $(this).val();

           });

            if($(arg).attr('id') == 'save_model'){
                create_info['action'] = 'save_model';
                var button_text = $(arg).text();
                $(arg).text('保存模板中.......')
            }else if($(arg).attr('id') == 'create_container' ){
                create_info['action'] = 'create_container';
                var button_text = $(arg).text();
                $(arg).text('创建容器中......')
            }

            create_info.dns = create_info.dns+',';    // 对输入一个DNS IP的话，在最后吗添加一个，方便后端处理
            console.log('create_info',create_info);
            var create_info_json = JSON.stringify(create_info);
            $.ajax({
                url:'{% url 'docker_containers_manage' %}',
                type:'GET',
                datatype:'json',
                token:csrftoken,
                data:{'create_info':create_info_json},
                success: function(callback) {
                    try {
                        alert('创建成功,容器ID：' + JSON.parse(callback).substring(0, 12));
                        console.log(callback);
                        fresh_all_containers();
                        $(arg).text(button_text);   // 把之前的按钮信息复位回去
                    }
                    catch(TypeError){
                        var error_dict = JSON.parse(callback);
                        for(var i in error_dict){
                            alert('创建失败,来自'+i+' 的报错信息如下:'+error_dict[i]);
                            console.log(error_dict[i])
                        }
                    } // end catch
                }, // end success
                error:function(callback){

                    console.log(JSON.parse(callback))
                }
            })
        }else{
            alert('输入信息不完整，容器名字必填');
            return false
        }
    }

    // 点击执行命令的按钮的时候，显示输入命令框
    function  show_entercmd_table() {
        var enter_cmd = $('#enter_cmd_div').html();
        var enter_cmd_button = $('#enter_cmd_button').html();
        $('#myModal').modal('toggle');
        $('.modal-body').html(enter_cmd);
        $('.modal-footer').html(enter_cmd_button);
    }