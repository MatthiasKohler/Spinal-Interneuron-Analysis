options(error = quote({
  dump.frames(to.file=T, dumpto='last.dump')
  load('last.dump.rda')
  print(last.dump)
  q()
}))

library(ggplot2)
library(grid)
library(gridExtra)
library(ggpubr)
library(data.table)
library(parallel)
library(doParallel)
library(uuid)
library(arules)
library(methods)
library(stringr)



associationRuleAnalysis <- function() {
    lines <- readLines('Results/AssociationRules.csv')
    idx <- grepl("Name", lines)
    m <- data.table(read.table(text=append(lines[1], lines[!idx]), sep = ',', header = TRUE))
    print(m)
   
    #Confidence Ia1 => Ib1 Support = 0.238938 p = 0.000000
    r <- "Confidence (.*) => (.*) Support = ([0-9]*.[0-9]*) p = ([0-9]*.[0-9]*)"

    m[, support      := (as.double(str_match(Name, r)[,4]))]
    m[, significance := (as.double(str_match(Name, r)[,5]))]
    m[, lhs          := factor(str_match(Name, r)[,2])]
    m[, rhs          := str_match(Name, r)[,3]]

    print(m)

    support <- unique(m[, c("lhs", "support")], by  = "lhs")
    print(support)

    confidence <- subset(m, original == T)[, c("lhs", "rhs", "significance", "support", "original", "Value")]
    confidence[order(support)]
    confidence$lhs <- factor(confidence$lhs)

    leveling <- unique(confidence, by = "lhs")[order(support)]
    print("Leveling")
    print(leveling)
    leveling$l <- 1:nrow(leveling)
    leveling <- leveling[, c("lhs", "l")];
    print(leveling)

    tmp <- leveling[, lhs]
    print(tmp)
    confidence$lhs <- factor(confidence$lhs, levels = tmp)
    confidence$rhs <- factor(confidence$rhs, levels = tmp)



    print("Confidence")
    print(confidence)

    bars <- ggplot(unique(confidence, by = 'lhs'), aes(x = lhs, y = support)) +
        geom_bar(stat = "identity") +
        theme_classic() +
        theme(axis.title.x = element_blank()) +
        theme(axis.text.x  = element_blank())
    print(bars)

    p <- ggplot(confidence, aes(x = lhs, y = rhs)) +
        theme_classic() +
        scale_y_discrete(position = "bottom") +        
        #geom_tile(aes(fill = confidence, alpha = -confidence.p)) +
        geom_tile(aes(fill = significance)) +
        coord_flip()

    #confidence$lhs <- factor(confidence$lhs, levels = confidence$support)
    
    #ggsave('Plots/test.pdf', p)


    plot_confidence <- function(rule) {
        print(rule)
        #l = as.character(rule[1])
        l = rule[1]
        #r = as.character(rule[2])
        r = rule[2]
        print("l")
        print(l)
        print("r")
        print(r)
        confidence.p = subset(confidence, lhs == l & rhs == r)$significance
        confidence.original = subset(m, lhs == l & rhs == r)[original == TRUE][1, Value]
        p2 <- ggplot(data = subset(m, lhs == l & rhs == r), aes(x = Value, y = freq)) +
                geom_line(color = 'red') +
                theme_classic() +          
                scale_x_continuous(limits = c(0, 1)) +
                geom_vline(xintercept = confidence.original, color = "green") +
                theme(axis.line=element_blank(),
                axis.title.x=element_blank(), axis.title.y=element_blank(),
                axis.text.x=element_blank(), axis.ticks.x=element_blank(),
                axis.text.y=element_blank(), axis.ticks.y=element_blank(),
                panel.background = element_rect(fill = "transparent",colour = NA),
                plot.background = element_rect(fill = "transparent",colour = NA),
                plot.margin=unit(c(0,0,0,0),"mm"))
        return(p2)
    }
    p2 <- plot_confidence(c("Skin1", "Skin2"))
    ggsave('Plots/test.pdf', p2)
#    
    axisMax = 16
    print(axisMax)
#  
    p <- p + annotation_custom(ggplotGrob(bars), xmin = axisMax + 2, ymin = -1.2, xmax = axisMax + 6, y = axisMax + 0.9)
#    
    rules <- unique(confidence[, c("lhs", "rhs")])
    print("rules")
    print(rules)

    #for(i in 1:3){#nrow(rules)) {
    for(i in 1:nrow(rules)) {
        item <- rules[i]
        #print(item)
        #print(as.character(item[,lhs]))
        #print(item[,rhs])
        conf <- plot_confidence(c(as.character(item[,lhs]), as.character(item[,rhs])))
        ggsave(paste("Plots/", i, '.pdf') , conf)
        x <- as.integer(confidence[lhs == item[,lhs]][1, lhs])
        y <- as.integer(confidence[lhs == item[,rhs]][1, lhs])
        #print(confidence[as.character(lhs) == as.character(item[,rhs])])
        print("xy")
        print(x)
        print(y)
        p <- p + annotation_custom(ggplotGrob(conf), xmin = x - 0.55, xmax = x + 0.45, 
                                                     ymin = y - 0.55, ymax = y + 0.45)
    }
   
    p <- p + theme(plot.margin=unit(c(5,0,0,0), "cm"),
                   panel.spacing=unit(c(0,0,0,0), "cm"))

    ggsave(p, file = 'Plots/AssociationRuleMatrix.pdf', width = 7, height = 8)
    #return(list(p1, p))

    return()
    plot_rule <- function(x) {
        #print(x)
        l <- x[1]
        r <- x[2]
        t <- subset(m, lhs == l & rhs == r)
        print(t)
        confidence.p = t[1, significance]
        confidence.original = t[original == TRUE][1, Value]
        support = t[1, support]
        title <- paste(l, "=>", r, sep = "")
        p <- ggplot(data = t, aes(x = Value, y = freq)) +
          ggtitle(paste(title, 'confidence', "support =", support, 'p =', confidence.p )) +
          geom_line() +
          scale_x_continuous(limits = c(0, 1)) +
          geom_vline(xintercept = confidence.original, color = "red")
        #ggarrange(p1, p2, p3, ncol = 1, nrow = 3)
        #return(list(p1, p2, p3))
        ggsave(paste("Plots/AssociationRules/", title, ".pdf", sep = ""), p)
    }
    #plot_rule("Skin1", "Skin2")
    apply(rules, 1, plot_rule)#, mc.cores = 8)
}

associationRuleAnalysis()
