function ShortPath_floyd(w,start,terminal)  
 %w----adjoin matrix, w=[0 50 inf inf inf;inf 0 inf inf 80 inf 30 0 20 inf;inf inf inf 0 70;65 inf 100 inf 0]; %start-----the start node;  
%terminal--------the end node;     

 n=size(w,1); 
 [D,path]=floyd1(w);
%调用floyd算法程序   
%找出任意两点之间的最短路径，并输出 
for i=1:n     
   for j=1:n       
    Min_path(i,j).distance=D(i,j);         
        %将i到j的最短路程赋值 Min_path(i,j).distance         
        %将i到j所经路径赋给Min_path(i,j).path         
  Min_path(i,j).path(1)=i;     k=1;         
 while Min_path(i,j).path(k)~=j            
       k=k+1;              
       Min_path(i,j).path(k)=path(Min_path(i,j).path(k-1),j);        
 end     
end 
end  
%{
s=sprintf('任意两点之间的最短路径如下：'); 
disp(s); 
for i=1:n     
for j=1:n         
   s=sprintf('从%d到%d的最短路径长度为：%d\n所经路径为：'...            
,i,j,Min_path(i,j).distance);         
disp(s);          
disp(Min_path(i,j).path); 
end
end
 %}
%找出在指定从start点到terminal点的最短路径，并输出  
str1=sprintf('从%d到%d的最短路径长度为：%d\n所经路径为：',...     
    start,terminal,Min_path(start,terminal).distance); 
disp(str1); 
disp(Min_path(start,terminal).path);  

 
%Foldy's Algorithm 算法程序 
function [D,path]=floyd1(a) 
n=size(a,1);  
D=a;path=zeros(n,n);%设置D和path的初值 
for i=1:n   
 for j=1:n        
   if D(i,j)~=inf          
       path(i,j)=j;%j是i的后点     
   end   
 end 
end  %做n次迭代，每次迭代都更新D(i,j)和path(i,j) 
for k=1:n    
for i=1:n      
 for j=1:n           
  if D(i,k)+D(k,j)<D(i,j)              
    D(i,j)=D(i,k)+D(k,j);%修改长度            
     path(i,j)=path(i,k);%修改路径        
    end       
end    
end 
end 
