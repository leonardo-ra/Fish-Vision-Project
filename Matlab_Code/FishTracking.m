clear all; close all; clc;
xyzt=load("fish_coordinates.csv");x=xyzt(:,1);y=xyzt(:,2);z=xyzt(:,3);t=xyzt(:,4);

for k=1:(length(t)-1)
plot3(x(1:k),y(1:k),z(1:k),'-*b'),hold on
ellipsoid(x(k),y(k),z(k),3.5,1.5,1.5)
axis([0 20 0 20 0 20]),grid on
title(strcat('Tempo=',num2str(t(k)),'s'))
xlabel('x (cm)');ylabel('y (cm)');zlabel('z (cm)');
drawnow,pause(0.5),hold off
k=k+1;
end