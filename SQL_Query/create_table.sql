CREATE TABLE `crypto_data`.`btcusdt-f`(
    `Datetime` DATETIME NOT NULL,
    `Open` FLOAT NOT NULL,
    `High` FLOAT NOT NULL,
    `Low` FLOAT NOT NULL,
    `Close` FLOAT NOT NULL,
    `Volume` FLOAT NOT NULL,
    `close_time` FLOAT NOT NULL,
    `quote_av` FLOAT NOT NULL,
    `trades` FLOAT NOT NULL,
    `tb_base_av` FLOAT NOT NULL,
    `tb_quote_av` FLOAT NOT NULL,
    `ignore` FLOAT NOT NULL,
    PRIMARY KEY(`Datetime`)
)

