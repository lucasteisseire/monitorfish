ALTER TABLE vessels 
  DROP COLUMN weight_authorized_on_deck,
  DROP COLUMN shipowner_name,
  DROP COLUMN shipowner_phones,
  DROP COLUMN shipowner_emails,
  DROP COLUMN fisher_name,
  DROP COLUMN fisher_phones,
  DROP COLUMN fisher_emails,
  ADD COLUMN vessel_emails varchar(100)[],
  ADD COLUMN vessel_phones varchar(100)[],
  ADD COLUMN proprietor_name varchar(200),
  ADD COLUMN proprietor_phones varchar(100)[],
  ADD COLUMN proprietor_emails varchar(100)[],
  ADD COLUMN operator_name varchar(200),
  ADD COLUMN operator_phones varchar(100)[],
  ADD COLUMN operator_emails varchar(100)[];