--
-- PostgreSQL database dump
--

-- Dumped from database version 14.3
-- Dumped by pg_dump version 14.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: guild_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guild_settings (
    id integer NOT NULL,
    language smallint,
    guild_did integer
);


ALTER TABLE public.guild_settings OWNER TO postgres;

--
-- Name: guild_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guild_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guild_settings_id_seq OWNER TO postgres;

--
-- Name: guild_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guild_settings_id_seq OWNED BY public.guild_settings.id;


--
-- Name: guilds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guilds (
    id integer NOT NULL,
    guild_id bigint NOT NULL
);


ALTER TABLE public.guilds OWNER TO postgres;

--
-- Name: guilds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guilds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guilds_id_seq OWNER TO postgres;

--
-- Name: guilds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guilds_id_seq OWNED BY public.guilds.id;


--
-- Name: guild_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_settings ALTER COLUMN id SET DEFAULT nextval('public.guild_settings_id_seq'::regclass);


--
-- Name: guilds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds ALTER COLUMN id SET DEFAULT nextval('public.guilds_id_seq'::regclass);


--
-- Name: guild_settings guild_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_settings
    ADD CONSTRAINT guild_settings_pkey PRIMARY KEY (id);


--
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (id);


--
-- Name: guild_settings guild_settings_guild_did_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_settings
    ADD CONSTRAINT guild_settings_guild_did_fkey FOREIGN KEY (guild_did) REFERENCES public.guilds(id);


--
-- PostgreSQL database dump complete
--

