# analysis.R
# Volatility and returns analysis for Commodity Compass
# Reads each commodity's price history CSV, computes daily log returns,
# rolling volatility, descriptive stats, and checks for volatility clustering.

library(dplyr)
library(ggplot2)

# ---- Setup ----
data_dir <- "data"
output_dir <- "output"
dir.create(output_dir, showWarnings = FALSE)

files <- list.files(data_dir, pattern = "\\.csv$", full.names = TRUE)

# ---- Helper: load one commodity's CSV and compute returns ----
load_and_process <- function(filepath) {
  df <- read.csv(filepath, stringsAsFactors = FALSE)
  
  # Date column looks like "2025-08-05 00:00:00-04:00" - we only need the
  # date part, so take the first 10 characters and parse that.
  df$Date <- as.Date(substr(df$Date, 1, 10))
  
  # Sort by date ascending, just in case
  df <- df[order(df$Date), ]
  
  # Daily log returns: log(price today / price yesterday)
  df$log_return <- c(NA, diff(log(df$Close)))
  
  # 20-day rolling volatility (standard deviation of log returns),
  # annualised by multiplying by sqrt(252) - the standard convention
  # for daily data (252 trading days/year)
  n <- nrow(df)
  rolling_vol <- rep(NA, n)
  window <- 20
  for (i in window:n) {
    rolling_vol[i] <- sd(df$log_return[(i - window + 1):i], na.rm = TRUE) * sqrt(252)
  }
  df$rolling_vol_annualised <- rolling_vol
  
  return(df)
}

# ---- Helper: descriptive stats for one commodity ----
summary_stats <- function(df, name) {
  returns <- na.omit(df$log_return)
  
  data.frame(
    commodity = name,
    mean_daily_return = mean(returns),
    annualised_vol = sd(returns) * sqrt(252),
    skewness = mean((returns - mean(returns))^3) / sd(returns)^3,
    kurtosis = mean((returns - mean(returns))^4) / sd(returns)^4,  # 3 = normal, >3 = fat tails
    n_obs = length(returns)
  )
}

# ---- Process every commodity ----
all_stats <- list()
all_data <- list()

for (f in files) {
  name <- tools::file_path_sans_ext(basename(f))
  df <- load_and_process(f)
  all_data[[name]] <- df
  all_stats[[name]] <- summary_stats(df, name)
}

stats_table <- bind_rows(all_stats)
print(stats_table)
write.csv(stats_table, file.path(output_dir, "summary_stats.csv"), row.names = FALSE)

# ---- Aluminium case study ----
# File is named ALI_F.csv based on the ticker "ALI=F"
alu <- all_data[["ALI_F"]]

# Plot: rolling volatility over time
p_vol <- ggplot(alu, aes(x = Date, y = rolling_vol_annualised)) +
  geom_line(color = "steelblue") +
  labs(title = "Aluminium: 20-Day Rolling Annualised Volatility",
       x = "Date", y = "Annualised Volatility") +
  theme_minimal()

ggsave(file.path(output_dir, "aluminium_rolling_vol.png"), p_vol, width = 8, height = 5)

# ACF plot on squared returns - the standard way to check for volatility
# clustering. If clustering exists, squared returns will show significant
# autocorrelation even though raw returns typically don't.
png(file.path(output_dir, "aluminium_acf_squared_returns.png"), width = 800, height = 500)
acf(na.omit(alu$log_return)^2, main = "Aluminium: ACF of Squared Returns (Volatility Clustering Check)")
dev.off()

# Plot: price history for reference
p_price <- ggplot(alu, aes(x = Date, y = Close)) +
  geom_line(color = "darkred") +
  labs(title = "Aluminium: Price History (13mo)", x = "Date", y = "Price (USD)") +
  theme_minimal()

ggsave(file.path(output_dir, "aluminium_price_history.png"), p_price, width = 8, height = 5)

cat("\nDone. Check the 'output' folder for:\n")
cat("  - summary_stats.csv (all commodities)\n")
cat("  - aluminium_rolling_vol.png\n")
cat("  - aluminium_acf_squared_returns.png\n")
cat("  - aluminium_price_history.png\n")
