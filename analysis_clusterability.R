#!/usr/bin/env Rscript

library(data.table)
library(cluster)
library(sigclust)

t <- data.table(read.table(file = './data_synaptology/Synaptology_HQ_tidy.csv', sep = ',', header = TRUE))
reliableData <- t[, grep("Skin1|Ia1|Ib1|Skin.2|Ia.2|Ib.2", names(t), value = T), with = F]

print(reliableData)

doSigclust <- function(data) {
    sc <- sigclust(data, 10000, nrep = 100, icovest = 2)
    print(sc)
}

doGapStat <- function(data) {
    K.max = nrow(unique(data))
    gapStat <- clusGap(data, FUN = kmeans, nstart = 200, iter.max = 10000,
                    K.max = K.max, B = 2000)
    print(gapStat)
}

doSigclust(reliableData)
doGapStat(reliableData)
