library(geoR)
library(splancs)
library(akima)
library(fields)
library(sp)
library(sf)
library(parallel)
#library(lattice)
#library(eda)

pdf("./F013B4_SoilAnalysis_KRT.pdf")

#Read in soil data
soildf<-read.table(file="./F013B4_SoilAnalysis_KRT.csv",header=TRUE,sep=',')
#print(sapply(soildf,typeof))

#Get convex hull polygon of sampling points
coords<-soildf[c("UTMX","UTMY")]
hull<-chull(coords$UTMX,coords$UTMY)
hull_coords<-coords[c(hull,hull[1]), ]
hull_sf<-st_as_sf(hull_coords,coords=c("UTMX","UTMY"))
hull_poly<-st_cast(st_combine(hull_sf),"POLYGON")

#Get prediction points (1 meter grid)
minx<-floor(min(soildf$UTMX))
maxx<-ceiling(max(soildf$UTMX))
miny<-floor(min(soildf$UTMY))
maxy<-ceiling(max(soildf$UTMY))
xvals<-seq(minx,maxx,1)
yvals<-seq(miny,maxy,1)
grid<-expand.grid(x=xvals,y=yvals)
colnames(grid)<-c("UTMX","UTMY")
grid<-lapply(grid,as.numeric)
grid<-data.frame(grid)
#print(dim(grid))

#Compute intersection of grid points with convex hull poly
points<-st_as_sf(grid,coords=c("UTMX","UTMY"))
intersection<-st_intersects(points,hull_poly)
#print(length(intersection))
grid$intersect<-lengths(intersection)
hullgrid<-subset(grid,intersect==1)
hullgrid<-subset(hullgrid,select=c(UTMX,UTMY))
rownames(hullgrid)<-NULL
#print(hullgrid)
#print(dim(hullgrid))

outdf<-data.frame(hullgrid)

depths<-c(20,60,100,140,180)
vars<-c('SLSND','SLSLT','SLCLY','SLSND2','SLSLT2','SLCLY2')

#Kriging
numcores<-detectCores()
dokrige <- function(geodata,locations,krige){
    result<-krige.conv(geodata=geodata,locations=locations,krige=krige)
    #print(result$predict[[1]])
    return(result$predict[[1]])
}

for (var in vars) {
    for (depth in depths) {
        header<-paste(var,sprintf("%03d",depth),sep="")
        data<-subset(soildf,Depth==depth)

        #Check for duplicates
        coords<-data[c("UTMX","UTMY")]
        sp_points<-SpatialPoints(coords)
        duplicates<-zerodist(sp_points)
        if (nrow(duplicates) > 0){
            print("Duplicate coordinates issue.")
            dev.off()
            stop()
        }

        #Setup geospatial data for evaluation
        gdata<-as.geodata(data,coords.col=c("UTMX","UTMY"),data.col=var)
        plot(gdata)

        #Evaluate optimal max.dist parameter for variogram
        minerror<-999999999
        for (max.dist in seq(75,100,1)){ #Maximum distance on variogram
            for (numbins in seq(5,9,1)){ #Number of bins on variogram
                var.gdata<-variog(gdata, uvec=numbins, max.dist=max.dist)
                #ini.cov.pars<-c(sd(gdata$data)**2,max.dist/2.)
                #Fix nugget for cases where range hits minimum
                limits<-pars.limits(phi=c(5,max.dist*0.75)) #Range limit
                if (header=="SLSND060"){
                    fit.gdata<-variofit(var.gdata,nugget=16.5, fix.nugget=TRUE, limits=limits)
                } else if (header=="SLSLT060"){
                    fit.gdata<-variofit(var.gdata,nugget=12.5, fix.nugget=TRUE, limits=limits)
                } else if (header=="SLSND2060"){
                    fit.gdata<-variofit(var.gdata,nugget=19.0, fix.nugget=TRUE, limits=limits)
                } else if (header=="SLSLT2020"){
                    fit.gdata<-variofit(var.gdata,nugget=7.5, fix.nugget=TRUE, limits=limits)
                } else if (header=="SLSLT2060"){
                    fit.gdata<-variofit(var.gdata,nugget=18.0, fix.nugget=TRUE, limits=limits)
                } else if (header=="SLCLY2180"){
                    fit.gdata<-variofit(var.gdata,nugget=9.0, fix.nugget=TRUE, limits=limits)
                } else {

                    fit.gdata<-variofit(var.gdata, limits=limits)
                }
                #print(attributes(fit.gdata))
                #print(fit.gdata$value)

                if (fit.gdata$value < minerror){
                    minerror = fit.gdata$value
                    opt.max.dist = max.dist
                    opt.numbins = numbins
                }
            }
        }

        var.gdata<-variog(gdata, uvec=opt.numbins, max.dist=opt.max.dist)
        #Default is matern spatial correlation model (fit.gdata$cov.model)
        #Fix nugget for cases where range hits minimum
        limits<-pars.limits(phi=c(5,opt.max.dist*0.75)) #Range limit
        if (header=="SLSND060"){
            fit.gdata<-variofit(var.gdata,nugget=16.5, fix.nugget=TRUE, limits=limits)
        } else if (header=="SLSLT060"){
            fit.gdata<-variofit(var.gdata,nugget=12.5, fix.nugget=TRUE, limits=limits)
        } else if (header=="SLSND2060"){
            fit.gdata<-variofit(var.gdata,nugget=19.0, fix.nugget=TRUE, limits=limits)
        } else if (header=="SLSLT2020"){
            fit.gdata<-variofit(var.gdata,nugget=7.5, fix.nugget=TRUE, limits=limits)
        } else if (header=="SLSLT2060"){
            fit.gdata<-variofit(var.gdata,nugget=18.0, fix.nugget=TRUE, limits=limits)
        } else if (header=="SLCLY2180"){
            fit.gdata<-variofit(var.gdata,nugget=9.0, fix.nugget=TRUE, limits=limits)
        } else {
            fit.gdata<-variofit(var.gdata, limits=limits)
        }

        plot(var.gdata,xlab="Distance (m)",ylab="Semi-variance",cex=1.5)
        lines(fit.gdata)
        xmin<-par("usr")[1]
        xmax<-par("usr")[2]
        ymin<-par("usr")[3]
        ymax<-par("usr")[4]
        x=xmin+(xmax-xmin)*0.75
        sill<-fit.gdata$cov.pars[1]+fit.gdata$nugget #Sigma^2 is partial sill. Sill=Partial sill + nugget
        text(x,ymin+(ymax-ymin)*0.35,paste("Sill = ",sprintf("%.2f",sill)))
        text(x,ymin+(ymax-ymin)*0.30,paste("Range = ",sprintf("%.2f",fit.gdata$cov.pars[2])))
        text(x,ymin+(ymax-ymin)*0.25,paste("Nugget = ",sprintf("%.2f",fit.gdata$nugget)))
        text(x,ymin+(ymax-ymin)*0.20,paste("Error = ",sprintf("%.2f",fit.gdata$value)))
        text(x,ymin+(ymax-ymin)*0.15,paste("opt.max.dist = ",sprintf("%d",opt.max.dist)))
        text(x,ymin+(ymax-ymin)*0.10,paste("opt.numbins = ",sprintf("%d",opt.numbins)))
        title(paste(header," Variogram"))
        kctrl<-krige.control(type.krige="ok",obj.model=fit.gdata)
        #krige.conv is a memory hog and slow. Need to parallelize.
        #krig.gdata<-krige.conv(geodata=gdata,locations=hullgrid,krige=kctrl) #Leads to high memory use
        #https://stackoverflow.com/questions/77672974/correct-use-of-mclapply
        krig.gdata<-mclapply(1:nrow(hullgrid),function(i) dokrige(gdata,hullgrid[i,],kctrl), mc.cores=numcores/2)
        df.gdata<-data.frame(unlist(krig.gdata)) #unlist is like Python flatten
        #print(df.gdata)
        #print(dim(df.gdata))
        #print(dim(outdf))
        colnames(df.gdata)<-c(header)
        outdf<-cbind(outdf,df.gdata)
    }
}

write.csv(outdf,file="./F013B4_SoilAnalysis_KRT_Interpolate.csv")

dev.off()
