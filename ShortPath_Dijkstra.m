function [path,short_distance]=ShortPath_Dijkstra(Input_weight,start,endpoint)
[row,col]=size(Input_weight);
%input detection 
if row~=col     
  error('input matrix is not a square matrix,input error ' ); 
end
if endpoint>row
 error('input parameter endpoint exceed the maximal point number'); 
end

%initialization 
s_path=[start]; 
 distance=inf*ones(1,row);distance(start)=0; 
flag(start)=start;temp=start;  

 while length(s_path)<row      
  pos=find(Input_weight(temp, : )~=inf);    
  for i=1:length(pos)         
   if (length(find(s_path==pos(i)))==0)&(distance(pos(i))>(distance(temp)+Input_weight(temp,pos(i)))) 
   distance(pos(i))=distance(temp)+Input_weight(temp,pos(i));             
  flag(pos(i))=temp;        
   end     
  end     
k=inf;      
 for i=1:row          
   if(length(find(s_path==i))==0)&(k>distance(i))            
    k=distance(i);             
    temp_2=i;         
    end     
 end      
s_path=[s_path,temp_2];     
temp=temp_2; 
 end

%output the result
path(1)=endpoint; i=1;  
while path(i)~=start      
   path(i+1)=flag(path(i));    
     i=i+1; 
end  
path(i)=start;  
path=path(end:-1:1);  
short_distance=distance(endpoint);
%将path倒过来输出
%试验：A=[0 7 1 6;inf 0 9 inf;4 4 0 2;1 inf inf 0]  [path,short_distance]=ShortPath_Dijkstra(A,4,2)
