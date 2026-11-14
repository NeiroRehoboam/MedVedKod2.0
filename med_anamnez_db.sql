--
-- PostgreSQL database dump
--

\restrict mmpl67KLxK3Mg8JdUv7tX5cN98Q0ucfPNgKnR5E2gHpLOCaRNbCcg1D7SebfXCO

-- Dumped from database version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: med_anamnez_db; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE med_anamnez_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8';


ALTER DATABASE med_anamnez_db OWNER TO postgres;

\unrestrict mmpl67KLxK3Mg8JdUv7tX5cN98Q0ucfPNgKnR5E2gHpLOCaRNbCcg1D7SebfXCO
\connect med_anamnez_db
\restrict mmpl67KLxK3Mg8JdUv7tX5cN98Q0ucfPNgKnR5E2gHpLOCaRNbCcg1D7SebfXCO

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: enum_istochnik_voprosa; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_istochnik_voprosa AS ENUM (
    'Система',
    'ИИ'
);


ALTER TYPE public.enum_istochnik_voprosa OWNER TO admin;

--
-- Name: enum_nasledstvennost; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_nasledstvennost AS ENUM (
    'Сердечно-сосудистые заболевания',
    'Онкология',
    'Диабет'
);


ALTER TYPE public.enum_nasledstvennost OWNER TO admin;

--
-- Name: enum_rezhim_priema; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_rezhim_priema AS ENUM (
    'Постоянно',
    'По необходимости'
);


ALTER TYPE public.enum_rezhim_priema OWNER TO admin;

--
-- Name: enum_srochnost; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_srochnost AS ENUM (
    'Экстренно',
    'Срочно',
    'Планово',
    'Самопомощь'
);


ALTER TYPE public.enum_srochnost OWNER TO admin;

--
-- Name: enum_status_alkogolya; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_status_alkogolya AS ENUM (
    'Не употребляет',
    'Иногда',
    'Регулярно'
);


ALTER TYPE public.enum_status_alkogolya OWNER TO admin;

--
-- Name: enum_status_kureniya; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_status_kureniya AS ENUM (
    'Не курит',
    'Курил ранее',
    'Курит'
);


ALTER TYPE public.enum_status_kureniya OWNER TO admin;

--
-- Name: enum_status_otveta; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_status_otveta AS ENUM (
    'Да',
    'Нет',
    'Неизвестно',
    'Не применимо'
);


ALTER TYPE public.enum_status_otveta OWNER TO admin;

--
-- Name: enum_status_sessii; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_status_sessii AS ENUM (
    'В процессе',
    'Завершена'
);


ALTER TYPE public.enum_status_sessii OWNER TO admin;

--
-- Name: enum_tip_allergii; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_tip_allergii AS ENUM (
    'Лекарственная',
    'Пищевая'
);


ALTER TYPE public.enum_tip_allergii OWNER TO admin;

--
-- Name: enum_tip_sobytiya; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.enum_tip_sobytiya AS ENUM (
    'Операция',
    'Госпитализация'
);


ALTER TYPE public.enum_tip_sobytiya OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: allergii_patsienta; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.allergii_patsienta (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    anamnez uuid,
    allergen uuid,
    svoy_variant bytea,
    tip_svoego_variants character varying(50)
);


ALTER TABLE public.allergii_patsienta OWNER TO admin;

--
-- Name: anamnez; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.anamnez (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patsient uuid,
    beremennost boolean,
    laktatsiya boolean,
    kurenie_status public.enum_status_kureniya,
    alkogol_status public.enum_status_alkogolya,
    data_obnovleniya timestamp with time zone DEFAULT now()
);


ALTER TABLE public.anamnez OWNER TO admin;

--
-- Name: bystrye_otvety; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.bystrye_otvety (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vopros uuid,
    tekst bytea,
    poryadkovyy_nomer integer
);


ALTER TABLE public.bystrye_otvety OWNER TO admin;

--
-- Name: lekarstva_patsienta; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lekarstva_patsienta (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    anamnez uuid,
    lekarstvo uuid,
    svoy_variant bytea,
    rezhim_priema public.enum_rezhim_priema
);


ALTER TABLE public.lekarstva_patsienta OWNER TO admin;

--
-- Name: meditsinskie_sobytiya; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.meditsinskie_sobytiya (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    anamnez uuid,
    tip_sobytiya public.enum_tip_sobytiya,
    opisaniye bytea,
    data_sobytiya date
);


ALTER TABLE public.meditsinskie_sobytiya OWNER TO admin;

--
-- Name: nasledstvennost_patsienta; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.nasledstvennost_patsienta (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    anamnez uuid,
    zabolevanie public.enum_nasledstvennost
);


ALTER TABLE public.nasledstvennost_patsienta OWNER TO admin;

--
-- Name: patsienty; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.patsienty (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    max_id character varying(64),
    data_registratsii timestamp with time zone DEFAULT now()
);


ALTER TABLE public.patsienty OWNER TO admin;

--
-- Name: rezultaty_marshtutizatsii; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.rezultaty_marshtutizatsii (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sessiya uuid,
    srochnost public.enum_srochnost,
    specialist uuid,
    obosnovaniye bytea,
    rekomendatsii bytea,
    data_sozdaniya timestamp with time zone DEFAULT now()
);


ALTER TABLE public.rezultaty_marshtutizatsii OWNER TO admin;

--
-- Name: sessii; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.sessii (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patsient uuid,
    nazvanie bytea,
    status public.enum_status_sessii,
    data_sozdaniya timestamp with time zone DEFAULT now(),
    data_obnovleniya timestamp with time zone DEFAULT now(),
    data_zaversheniya timestamp with time zone
);


ALTER TABLE public.sessii OWNER TO admin;

--
-- Name: spravochnik_allergenov; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.spravochnik_allergenov (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nazvanie character varying(200),
    tip public.enum_tip_allergii,
    aktivno boolean DEFAULT true
);


ALTER TABLE public.spravochnik_allergenov OWNER TO admin;

--
-- Name: spravochnik_lekarstv; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.spravochnik_lekarstv (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nazvanie character varying(200),
    aktivno boolean DEFAULT true
);


ALTER TABLE public.spravochnik_lekarstv OWNER TO admin;

--
-- Name: spravochnik_specialistov; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.spravochnik_specialistov (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nazvanie character varying(150),
    aktivno boolean DEFAULT true
);


ALTER TABLE public.spravochnik_specialistov OWNER TO admin;

--
-- Name: spravochnik_zabolevaniy; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.spravochnik_zabolevaniy (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nazvanie character varying(200),
    aktivno boolean DEFAULT true
);


ALTER TABLE public.spravochnik_zabolevaniy OWNER TO admin;

--
-- Name: voprosy_sessii; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.voprosy_sessii (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sessiya uuid,
    tekst_voprosa bytea,
    tekst_otveta bytea,
    poryadkovyy_nomer integer,
    istochnik public.enum_istochnik_voprosa,
    data_sozdaniya timestamp with time zone DEFAULT now(),
    data_otveta timestamp with time zone
);


ALTER TABLE public.voprosy_sessii OWNER TO admin;

--
-- Name: zabolevaniya_patsienta; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.zabolevaniya_patsienta (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    anamnez uuid,
    zabolevanie uuid,
    svoy_variant bytea
);


ALTER TABLE public.zabolevaniya_patsienta OWNER TO admin;

--
-- Data for Name: allergii_patsienta; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.allergii_patsienta (id, anamnez, allergen, svoy_variant, tip_svoego_variants) FROM stdin;
\.


--
-- Data for Name: anamnez; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.anamnez (id, patsient, beremennost, laktatsiya, kurenie_status, alkogol_status, data_obnovleniya) FROM stdin;
\.


--
-- Data for Name: bystrye_otvety; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.bystrye_otvety (id, vopros, tekst, poryadkovyy_nomer) FROM stdin;
\.


--
-- Data for Name: lekarstva_patsienta; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lekarstva_patsienta (id, anamnez, lekarstvo, svoy_variant, rezhim_priema) FROM stdin;
\.


--
-- Data for Name: meditsinskie_sobytiya; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.meditsinskie_sobytiya (id, anamnez, tip_sobytiya, opisaniye, data_sobytiya) FROM stdin;
\.


--
-- Data for Name: nasledstvennost_patsienta; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.nasledstvennost_patsienta (id, anamnez, zabolevanie) FROM stdin;
\.


--
-- Data for Name: patsienty; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.patsienty (id, max_id, data_registratsii) FROM stdin;
\.


--
-- Data for Name: rezultaty_marshtutizatsii; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.rezultaty_marshtutizatsii (id, sessiya, srochnost, specialist, obosnovaniye, rekomendatsii, data_sozdaniya) FROM stdin;
\.


--
-- Data for Name: sessii; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.sessii (id, patsient, nazvanie, status, data_sozdaniya, data_obnovleniya, data_zaversheniya) FROM stdin;
\.


--
-- Data for Name: spravochnik_allergenov; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.spravochnik_allergenov (id, nazvanie, tip, aktivno) FROM stdin;
\.


--
-- Data for Name: spravochnik_lekarstv; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.spravochnik_lekarstv (id, nazvanie, aktivno) FROM stdin;
\.


--
-- Data for Name: spravochnik_specialistov; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.spravochnik_specialistov (id, nazvanie, aktivno) FROM stdin;
\.


--
-- Data for Name: spravochnik_zabolevaniy; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.spravochnik_zabolevaniy (id, nazvanie, aktivno) FROM stdin;
\.


--
-- Data for Name: voprosy_sessii; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.voprosy_sessii (id, sessiya, tekst_voprosa, tekst_otveta, poryadkovyy_nomer, istochnik, data_sozdaniya, data_otveta) FROM stdin;
\.


--
-- Data for Name: zabolevaniya_patsienta; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.zabolevaniya_patsienta (id, anamnez, zabolevanie, svoy_variant) FROM stdin;
\.


--
-- Name: allergii_patsienta allergii_patsienta_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.allergii_patsienta
    ADD CONSTRAINT allergii_patsienta_pkey PRIMARY KEY (id);


--
-- Name: anamnez anamnez_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.anamnez
    ADD CONSTRAINT anamnez_pkey PRIMARY KEY (id);


--
-- Name: bystrye_otvety bystrye_otvety_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bystrye_otvety
    ADD CONSTRAINT bystrye_otvety_pkey PRIMARY KEY (id);


--
-- Name: lekarstva_patsienta lekarstva_patsienta_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lekarstva_patsienta
    ADD CONSTRAINT lekarstva_patsienta_pkey PRIMARY KEY (id);


--
-- Name: meditsinskie_sobytiya meditsinskie_sobytiya_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.meditsinskie_sobytiya
    ADD CONSTRAINT meditsinskie_sobytiya_pkey PRIMARY KEY (id);


--
-- Name: nasledstvennost_patsienta nasledstvennost_patsienta_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.nasledstvennost_patsienta
    ADD CONSTRAINT nasledstvennost_patsienta_pkey PRIMARY KEY (id);


--
-- Name: patsienty patsienty_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.patsienty
    ADD CONSTRAINT patsienty_pkey PRIMARY KEY (id);


--
-- Name: rezultaty_marshtutizatsii rezultaty_marshtutizatsii_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.rezultaty_marshtutizatsii
    ADD CONSTRAINT rezultaty_marshtutizatsii_pkey PRIMARY KEY (id);


--
-- Name: sessii sessii_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessii
    ADD CONSTRAINT sessii_pkey PRIMARY KEY (id);


--
-- Name: spravochnik_allergenov spravochnik_allergenov_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.spravochnik_allergenov
    ADD CONSTRAINT spravochnik_allergenov_pkey PRIMARY KEY (id);


--
-- Name: spravochnik_lekarstv spravochnik_lekarstv_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.spravochnik_lekarstv
    ADD CONSTRAINT spravochnik_lekarstv_pkey PRIMARY KEY (id);


--
-- Name: spravochnik_specialistov spravochnik_specialistov_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.spravochnik_specialistov
    ADD CONSTRAINT spravochnik_specialistov_pkey PRIMARY KEY (id);


--
-- Name: spravochnik_zabolevaniy spravochnik_zabolevaniy_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.spravochnik_zabolevaniy
    ADD CONSTRAINT spravochnik_zabolevaniy_pkey PRIMARY KEY (id);


--
-- Name: voprosy_sessii voprosy_sessii_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.voprosy_sessii
    ADD CONSTRAINT voprosy_sessii_pkey PRIMARY KEY (id);


--
-- Name: zabolevaniya_patsienta zabolevaniya_patsienta_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.zabolevaniya_patsienta
    ADD CONSTRAINT zabolevaniya_patsienta_pkey PRIMARY KEY (id);


--
-- Name: allergii_patsienta allergii_patsienta_allergen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.allergii_patsienta
    ADD CONSTRAINT allergii_patsienta_allergen_fkey FOREIGN KEY (allergen) REFERENCES public.spravochnik_allergenov(id);


--
-- Name: allergii_patsienta allergii_patsienta_anamnez_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.allergii_patsienta
    ADD CONSTRAINT allergii_patsienta_anamnez_fkey FOREIGN KEY (anamnez) REFERENCES public.anamnez(id);


--
-- Name: anamnez anamnez_patsient_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.anamnez
    ADD CONSTRAINT anamnez_patsient_fkey FOREIGN KEY (patsient) REFERENCES public.patsienty(id);


--
-- Name: bystrye_otvety bystrye_otvety_vopros_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bystrye_otvety
    ADD CONSTRAINT bystrye_otvety_vopros_fkey FOREIGN KEY (vopros) REFERENCES public.voprosy_sessii(id);


--
-- Name: lekarstva_patsienta lekarstva_patsienta_anamnez_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lekarstva_patsienta
    ADD CONSTRAINT lekarstva_patsienta_anamnez_fkey FOREIGN KEY (anamnez) REFERENCES public.anamnez(id);


--
-- Name: lekarstva_patsienta lekarstva_patsienta_lekarstvo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lekarstva_patsienta
    ADD CONSTRAINT lekarstva_patsienta_lekarstvo_fkey FOREIGN KEY (lekarstvo) REFERENCES public.spravochnik_lekarstv(id);


--
-- Name: meditsinskie_sobytiya meditsinskie_sobytiya_anamnez_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.meditsinskie_sobytiya
    ADD CONSTRAINT meditsinskie_sobytiya_anamnez_fkey FOREIGN KEY (anamnez) REFERENCES public.anamnez(id);


--
-- Name: nasledstvennost_patsienta nasledstvennost_patsienta_anamnez_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.nasledstvennost_patsienta
    ADD CONSTRAINT nasledstvennost_patsienta_anamnez_fkey FOREIGN KEY (anamnez) REFERENCES public.anamnez(id);


--
-- Name: rezultaty_marshtutizatsii rezultaty_marshtutizatsii_sessiya_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.rezultaty_marshtutizatsii
    ADD CONSTRAINT rezultaty_marshtutizatsii_sessiya_fkey FOREIGN KEY (sessiya) REFERENCES public.sessii(id);


--
-- Name: rezultaty_marshtutizatsii rezultaty_marshtutizatsii_specialist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.rezultaty_marshtutizatsii
    ADD CONSTRAINT rezultaty_marshtutizatsii_specialist_fkey FOREIGN KEY (specialist) REFERENCES public.spravochnik_specialistov(id);


--
-- Name: sessii sessii_patsient_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessii
    ADD CONSTRAINT sessii_patsient_fkey FOREIGN KEY (patsient) REFERENCES public.patsienty(id);


--
-- Name: voprosy_sessii voprosy_sessii_sessiya_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.voprosy_sessii
    ADD CONSTRAINT voprosy_sessii_sessiya_fkey FOREIGN KEY (sessiya) REFERENCES public.sessii(id);


--
-- Name: zabolevaniya_patsienta zabolevaniya_patsienta_anamnez_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.zabolevaniya_patsienta
    ADD CONSTRAINT zabolevaniya_patsienta_anamnez_fkey FOREIGN KEY (anamnez) REFERENCES public.anamnez(id);


--
-- Name: zabolevaniya_patsienta zabolevaniya_patsienta_zabolevanie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.zabolevaniya_patsienta
    ADD CONSTRAINT zabolevaniya_patsienta_zabolevanie_fkey FOREIGN KEY (zabolevanie) REFERENCES public.spravochnik_zabolevaniy(id);


--
-- PostgreSQL database dump complete
--

\unrestrict mmpl67KLxK3Mg8JdUv7tX5cN98Q0ucfPNgKnR5E2gHpLOCaRNbCcg1D7SebfXCO

