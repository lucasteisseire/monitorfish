WITH pagn AS (
    SELECT
        pagn.id_nav_pa, 
        cpagn.libelle_court AS sailing_type
    FROM NAVPRO.NAV_PA_GN pagn
    JOIN COMMUN.C_CODE_GENRE_NAVIGATION cpagn
    ON pagn.idc_genre_navigation = cpagn.idc_genre_navigation
),

filtered_pa AS (
    SELECT
        id_nav_flotteur,
        id_adm_intervenant,
        id_nav_pa
    FROM NAVPRO.NAV_PA pa
    WHERE (pa.est_dernier = 1) AND (pa.idc_nav_categ_armement = 1) AND (pa.idc_nav_statut_pa IN (1, 2))
),

pa AS (
    SELECT
        filtered_pa.id_nav_flotteur,
        filtered_pa.id_adm_intervenant,
        LISTAGG(pagn.sailing_type, ', ') WITHIN GROUP(ORDER BY pagn.sailing_type) AS sailing_types
    FROM filtered_pa
    JOIN pagn
    ON pagn.id_nav_pa = filtered_pa.id_nav_pa
    GROUP BY filtered_pa.id_nav_flotteur, filtered_pa.id_adm_intervenant
),

e AS (
    SELECT
        id_adm_entreprise AS id_adm,
        raison_sociale AS name,
        email,
        telephone AS phone,
        tel_mobile AS mobile_phone
    FROM ADM.ADM_ENTREPRISE
), 

a AS (
    SELECT
        id_adm_administre AS id_adm,
        nom || DECODE(prenom, NULL, '', ' ') || prenom as name,
        email, 
        telephone AS phone, 
        tel_mobile AS mobile_phone
    FROM ADM.ADM_ADMINISTRE
),

adm AS (
    SELECT * FROM e
    UNION ALL
    SELECT * FROM a
),

nfp AS (
    SELECT
        nfp.id_nav_navire_francais AS id_nav_navire_francais,
        nfp.numero_cfr AS cfr_nfp,
        eng_1.libelle AS fishing_gear_main,
        eng_2.libelle AS fishing_gear_secondary,
        eng_3.libelle AS fishing_gear_third
    FROM NAVPRO.NAV_FR_PECHE nfp
    LEFT JOIN VENUS.F_CODE_ENGIN eng_1
    ON nfp.idc_engin_principal = eng_1.idc_engin
    LEFT JOIN VENUS.F_CODE_ENGIN eng_2
    ON nfp.idc_engin_secondaire = eng_2.idc_engin 
    LEFT JOIN VENUS.F_CODE_ENGIN eng_3
    ON nfp.idc_autre_engin_1 = eng_3.idc_engin
),

nf AS (
    SELECT 
        id_nav_navire_francais,
        id_nav_flotteur,
        longueur_hors_tout,
        largeur,
        jauge_londres,
        puissance_propulsive,
        num_telephone,
        email1,
        email2,
        tel_fixe_2_contact_navire,
        tel_fixe_3_contact_navire,
        tel_mobile_contact_navire,
        idc_quartier,
        idc_type_navire,
        idc_port_exploitation,
        idc_pays_navire,
        id_adm_interv_exploitant,
        id_adm_interv_proprietaire
    FROM NAVPRO.NAV_NAVIRE_FRANCAIS
    WHERE est_dernier = 1
)

SELECT

	nf.id_nav_navire_francais AS id_nav_navire_francais_nf,
	nf.id_nav_flotteur AS id_nav_flotteur_nf,
	nf.longueur_hors_tout AS length_nf,
	nf.largeur AS width_nf,
	nf.jauge_londres AS gauge_nf,
	nf.puissance_propulsive AS power_nf,
	nf.num_telephone AS fisher_phone_1_nf,
	nf.email1 AS fisher_email_nf,
	nf.email2 AS fisher_email_1_nf,
	nf.tel_fixe_2_contact_navire AS fisher_phone_2_nf,
	nf.tel_fixe_3_contact_navire AS fisher_phone_3_nf,
	nf.tel_mobile_contact_navire AS fisher_phone_nf,
	ctn.libelle_minus AS vessel_type_nf,
	cpt.libelle AS registry_port_nf,
	pa.sailing_types as sailing_types_nf,
    adm_fisher.name AS fisher_name_nf,
    adm_fisher.email AS fisher_email_2_nf,
    adm_fisher.phone AS fisher_phone_4_nf,
    adm_fisher.mobile_phone AS fisher_phone_5_nf,
    adm_shipowner.name AS shipowner_name_nf,
    adm_shipowner.email AS shipowner_email_nf,
    adm_shipowner.phone AS shipowner_phone_nf,
    adm_shipowner.mobile_phone AS shipowner_phone_1_nf,
    nfp.id_nav_navire_francais AS id_nav_navire_francais_nfp,
    nfp.fishing_gear_main AS fishing_gear_main_nfp,
    nfp.fishing_gear_secondary AS fishing_gear_secondary_nfp,
    nfp.fishing_gear_third AS fishing_gear_third_nfp
FROM nf
LEFT JOIN NAVPRO.NAV_CODE_TYPE_NAVIRE ctn
ON nf.idc_type_navire = ctn.idc_type_navire
LEFT JOIN COMMUN.C_CODE_PORT cpt
ON cpt.idc_port = nf.idc_port_exploitation
LEFT JOIN COMMUN.C_CODE_QUARTIER cq
ON cq.idc_quartier = nf.idc_quartier
LEFT JOIN pa
ON pa.id_nav_flotteur = nf.id_nav_flotteur AND nf.id_adm_interv_exploitant = pa.id_adm_intervenant
LEFT JOIN adm adm_fisher
ON adm_fisher.id_adm = nf.id_adm_interv_exploitant
LEFT JOIN adm adm_shipowner
ON adm_shipowner.id_adm = nf.id_adm_interv_proprietaire
LEFT JOIN nfp
ON nfp.id_nav_navire_francais = nf.id_nav_navire_francais