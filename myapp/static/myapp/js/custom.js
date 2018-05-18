// 样式处理


// 1. 聚焦搜索框后placeholder消失, 学会两招！data当做全局变量，连续两个函数打点连接
$('#search-box').focus(function(){
   $(this).data('placeholder',$(this).attr('placeholder'))
          .attr('placeholder','');
}).blur(function(){
   $(this).attr('placeholder',$(this).data('placeholder'));
});
