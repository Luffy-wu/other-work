function ShortPath_floyd(w,start,terminal)  
 %w----adjoin matrix, w=[0 50 inf inf inf;inf 0 inf inf 80 inf 30 0 20 inf;inf inf inf 0 70;65 inf 100 inf 0]; %start-----the start node;  
%terminal--------the end node;     

 n=size(w,1); 
 [D,path]=floyd1(w);
%����floyd�㷨����   
%�ҳ���������֮������·��������� 
for i=1:n     
   for j=1:n       
    Min_path(i,j).distance=D(i,j);         
        %��i��j�����·�̸�ֵ Min_path(i,j).distance         
        %��i��j����·������Min_path(i,j).path         
  Min_path(i,j).path(1)=i;     k=1;         
 while Min_path(i,j).path(k)~=j            
       k=k+1;              
       Min_path(i,j).path(k)=path(Min_path(i,j).path(k-1),j);        
 end     
end 
end  
%{
s=sprintf('��������֮������·�����£�'); 
disp(s); 
for i=1:n     
for j=1:n         
   s=sprintf('��%d��%d�����·������Ϊ��%d\n����·��Ϊ��'...            
,i,j,Min_path(i,j).distance);         
disp(s);          
disp(Min_path(i,j).path); 
end
end
 %}
%�ҳ���ָ����start�㵽terminal������·���������  
str1=sprintf('��%d��%d�����·������Ϊ��%d\n����·��Ϊ��',...     
    start,terminal,Min_path(start,terminal).distance); 
disp(str1); 
disp(Min_path(start,terminal).path);  

 
%Foldy's Algorithm �㷨���� 
function [D,path]=floyd1(a) 
n=size(a,1);  
D=a;path=zeros(n,n);%����D��path�ĳ�ֵ 
for i=1:n   
 for j=1:n        
   if D(i,j)~=inf          
       path(i,j)=j;%j��i�ĺ��     
   end   
 end 
end  %��n�ε�����ÿ�ε���������D(i,j)��path(i,j) 
for k=1:n    
for i=1:n      
 for j=1:n           
  if D(i,k)+D(k,j)<D(i,j)              
    D(i,j)=D(i,k)+D(k,j);%�޸ĳ���            
     path(i,j)=path(i,k);%�޸�·��        
    end       
end    
end 
end 
