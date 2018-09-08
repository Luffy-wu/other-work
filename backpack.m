function [U]=backpack(S,V,C)
%S=[2 3 4 5]; V=[3 4 5 7];C=9
n=length(S);
for i=1:(n+1)
 U(i,1)=0;
end
for j=1:(C+1)
    U(1,j)=0;  %≥ı ºªØ
end
for i=2:(n+1)
    for j=2:(C+1)
        U(i,j)=U(i-1,j);
        if (S(i-1)<=(j-1))
           if(U(i,j)<(U(i-1,j-S(i-1))+V(i-1)))
               U(i,j)=(U(i-1,j-S(i-1))+V(i-1));
           end
        end
    end
end

