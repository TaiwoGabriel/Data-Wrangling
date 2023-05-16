
library("dplyr")

prep_epr <- function(input_folder){
   files <- file.path(input_folder, "geoepr", "data", c("GeoEPR.shp","EPR-2018.1.1.csv"))
   geoepr <- sf::read_sf(files[1])
   geoepr <- sf::st_transform(geoepr, crs = priogrid::prio_crs()) %>%
     dplyr::mutate(year = purrr::map2(from, to, `:`)) %>%
     tidyr::unnest(year)

   epr <- read.csv(files[2], stringsAsFactors = FALSE)

   epr <- epr %>%
     dplyr::mutate(epr_excluded = 1,
                    year = purrr::map2(from, to, `:`)) %>%
     tidyr::unnest(year)

   geoepr <- geoepr %>%
      dplyr::right_join(epr, by = c("year", "gwgroupid", "gwid")) %>%
      dplyr::arrange(gwgroupid, year) %>%
      dplyr::group_by(gwgroupid) %>%
      dplyr::ungroup() %>%
      dplyr::select(gwid, gwgroupid, year, epr_excluded, geometry) %>%
      dplyr::filter(!sf::st_is_empty(geometry))

   geoepr <- sf::st_cast(geoepr, to = "MULTIPOLYGON")

   return(geoepr)
}

panel_to_pg <- function(df, timevar, variable, need_aggregation, missval, fun){
  time_fact <- factor(df[[timevar]])

  sdf <- dplyr::select(df, !!variable)
  sdf_list <- base::split(sdf, time_fact, sep = "_")
  rast_list <- parallel::mclapply(sdf_list, vector_to_pg, variable = variable, need_aggregation = need_aggregation, missval = missval, fun = fun)

  pg_tibble <- parallel::mclapply(rast_list, raster_to_tibble, add_pg_index = TRUE)

  add_timevar <- function(df, time, timevar){
    df[[timevar]] <- time
    return(df)
  }

  pg_tibble <- purrr::map2_dfr(pg_tibble, names(pg_tibble), add_timevar, timevar = timevar)
  return(pg_tibble)
}

gen_excluded <- function(input_folder, variable = "epr_excluded"){
   excluded <- prep_epr(input_folder)

   excluded <- priogrid::panel_to_pg(excluded,
                                     timevar = "year",
                                     variable = variable,
                                     need_aggregation = TRUE,
                                     fun = "sum")

   return(excluded)

}
gen_excluded("/input/r_file", variable = "epr_excluded")

