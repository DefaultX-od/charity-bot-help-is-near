--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Ubuntu 15.7-0ubuntu0.23.10.1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.1)

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

--
-- Name: add_user(bigint, character varying, character varying, character varying, bigint, character varying); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.add_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _contact_str character varying) RETURNS void
    LANGUAGE sql
    AS $$
	insert into users(id_user, name, surname, address, phone, contact_str)
	values(_id_user, _name, _surname, _address, _phone, _contact_str);
$$;


ALTER FUNCTION public.add_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _contact_str character varying) OWNER TO defaultxod;

--
-- Name: assign_task(bigint, bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.assign_task(_id_task bigint, _id_vol bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set id_vol=_id_vol, status='в работе' where id_task=_id_task and status='создано';
$$;


ALTER FUNCTION public.assign_task(_id_task bigint, _id_vol bigint) OWNER TO defaultxod;

--
-- Name: create_category(character varying, character varying); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.create_category(_name character varying, _description character varying) RETURNS void
    LANGUAGE sql
    AS $$
	insert into category (name, description)
	values(_name, _description)
$$;


ALTER FUNCTION public.create_category(_name character varying, _description character varying) OWNER TO defaultxod;

--
-- Name: create_task(bigint, bigint, character varying, text, date); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.create_task(_id_desp bigint, _id_category bigint, _name character varying, _description text, _expire_date date) RETURNS void
    LANGUAGE sql
    AS $$
	insert into tasks (id_desp, id_category, status, name, description, expire_date)
	values(_id_desp, _id_category, 'создано',_name, _description, _expire_date)
$$;


ALTER FUNCTION public.create_task(_id_desp bigint, _id_category bigint, _name character varying, _description text, _expire_date date) OWNER TO defaultxod;

--
-- Name: delete_category(integer); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.delete_category(_id_category integer) RETURNS void
    LANGUAGE sql
    AS $$
	delete from tasks where id_category=_id_category;
	delete from category where id_category=_id_category;
$$;


ALTER FUNCTION public.delete_category(_id_category integer) OWNER TO defaultxod;

--
-- Name: delete_task(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.delete_task(_id_task bigint) RETURNS void
    LANGUAGE sql
    AS $$
	delete from tasks where id_task=_id_task
$$;


ALTER FUNCTION public.delete_task(_id_task bigint) OWNER TO defaultxod;

--
-- Name: delete_user(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.delete_user(_id_user bigint) RETURNS void
    LANGUAGE sql
    AS $$
	delete from tasks where id_vol = _id_user or id_desp = _id_user;
	delete from users where id_user = _id_user;
$$;


ALTER FUNCTION public.delete_user(_id_user bigint) OWNER TO defaultxod;

--
-- Name: edit_user(bigint, character varying, character varying, character varying, bigint, character varying); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.edit_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _user_name character varying) RETURNS void
    LANGUAGE sql
    AS $$
	update users set name=_name, surname=_surname,
	address=_address, phone=_phone, tg_usr_name=_user_name
	where id_user = _id_user;
$$;


ALTER FUNCTION public.edit_user(_id_user bigint, _name character varying, _surname character varying, _address character varying, _phone bigint, _user_name character varying) OWNER TO defaultxod;

--
-- Name: get_desp_by_task_id(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_desp_by_task_id(_id_task bigint) RETURNS TABLE(userid bigint)
    LANGUAGE sql
    AS $$
		select id_desp from tasks where id_task=_id_task;
$$;


ALTER FUNCTION public.get_desp_by_task_id(_id_task bigint) OWNER TO defaultxod;

--
-- Name: get_task_by_vol_id(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_task_by_vol_id(_id_vol bigint) RETURNS TABLE(id_task bigint)
    LANGUAGE sql
    AS $$
	select id_task from tasks where id_vol = _id_vol and status = 'в работе';
$$;


ALTER FUNCTION public.get_task_by_vol_id(_id_vol bigint) OWNER TO defaultxod;

--
-- Name: get_task_full(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_task_full(_id_task bigint) RETURNS TABLE(id integer, task_text text)
    LANGUAGE sql
    AS $$
	select
	t.id_task,
	'Категория: '||c.name||
	chr(10)||chr(10)||'Название: '||t.name||
	chr(10)||chr(10)||'Описние: '||t.description||
	chr(10)||chr(10)||'Выполнить до: '||t.expire_date||
	chr(10)||chr(10)||'Контакты: '||u.contact_str
	from tasks t join category c on t.id_category = c.id_category
	join users u on u.id_user= t.id_desp
	where t.id_task=_id_task;
$$;


ALTER FUNCTION public.get_task_full(_id_task bigint) OWNER TO defaultxod;

--
-- Name: get_task_light(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_task_light(_id_category bigint) RETURNS TABLE(id integer, task_text text)
    LANGUAGE sql
    AS $$
	update tasks set status='не выполнено' where expire_date<NOW() - INTERVAL '1 DAY';

	select id_task, name from tasks
	where id_category=_id_category and status = 'создано';
$$;


ALTER FUNCTION public.get_task_light(_id_category bigint) OWNER TO defaultxod;

--
-- Name: get_tasks_by_desp_id(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_tasks_by_desp_id(id bigint) RETURNS TABLE(id bigint, task text)
    LANGUAGE sql
    AS $$
	select
	t.id_task,
	'Категория: '||c.name||
	chr(10)||chr(10)||'Название: '||t.name||
	chr(10)||chr(10)||'Описние: '||t.description||
	chr(10)||chr(10)||'Выполнить до: '||expire_date
	from tasks t left join category c on t.id_category = c.id_category
	where t.id_desp = id and (status = 'создано' or status = 'в работе')
$$;


ALTER FUNCTION public.get_tasks_by_desp_id(id bigint) OWNER TO defaultxod;

--
-- Name: get_tasks_wip(); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_tasks_wip() RETURNS TABLE(id integer, task_text text)
    LANGUAGE sql
    AS $$
	select
	t.id_task,
	'Категория: '||c.name||
	chr(10)||chr(10)||'Название: '||t.name||
	chr(10)||chr(10)||'Описние: '||t.description||
	chr(10)||chr(10)||'Выполнить до: '||t.expire_date||
	chr(10)||chr(10)||'Контакты: '||u.contact_str
	from tasks t join category c on t.id_category = c.id_category
	join users u on u.id_user= t.id_desp
	where t.status = 'создано' or t.status = 'в работе'
$$;


ALTER FUNCTION public.get_tasks_wip() OWNER TO defaultxod;

--
-- Name: get_user_info(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_user_info(_id_user bigint) RETURNS TABLE(id bigint, user_info text)
    LANGUAGE sql
    AS $$
	select
	id_user,
	'Фамилия: ' || u.surname ||
	chr(10)||chr(10)||'Имя: ' || u.name ||
	chr(10)||chr(10)||'Роль: ' || ut.ru_user_type_name ||
	chr(10)||chr(10)||'Город: ' || u.address ||
	chr(10)||chr(10)||'Контакт: ' || u.contact_str	
	from users u join user_types ut on u.id_user_type = ut.id_user_type
	where u.id_user::int8 = _id_user::int8 ;
$$;


ALTER FUNCTION public.get_user_info(_id_user bigint) OWNER TO defaultxod;

--
-- Name: get_user_type(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_user_type(_id_user bigint) RETURNS text
    LANGUAGE sql
    AS $$
	select ut.user_type_name from users u 
	inner join user_types ut on u.id_user_type = ut.id_user_type where u.id_user=_id_user;
$$;


ALTER FUNCTION public.get_user_type(_id_user bigint) OWNER TO defaultxod;

--
-- Name: get_users_by_type(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_users_by_type(_id_user_type bigint) RETURNS TABLE(id bigint, full_name text)
    LANGUAGE sql
    AS $$
	select id_user::int8,
	surname || ' ' || name from users where id_user_type::int8=_id_user_type::int8;
$$;


ALTER FUNCTION public.get_users_by_type(_id_user_type bigint) OWNER TO defaultxod;

--
-- Name: get_vol_by_task_id(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.get_vol_by_task_id(_id_task bigint) RETURNS TABLE(userid bigint)
    LANGUAGE sql
    AS $$
		select id_vol from tasks where id_task=_id_task;
$$;


ALTER FUNCTION public.get_vol_by_task_id(_id_task bigint) OWNER TO defaultxod;

--
-- Name: is_vol_on_task(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.is_vol_on_task(_id_vol bigint) RETURNS TABLE(num integer)
    LANGUAGE sql
    AS $$
	select (count(id_vol)) as num from tasks where id_vol=_id_vol and status = 'в работе';
$$;


ALTER FUNCTION public.is_vol_on_task(_id_vol bigint) OWNER TO defaultxod;

--
-- Name: remove_vol_from_task(bigint, bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.remove_vol_from_task(_id_task bigint, _id_vol bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set id_vol = NULL, status='создано' where id_task=_id_task and status='в работе';
$$;


ALTER FUNCTION public.remove_vol_from_task(_id_task bigint, _id_vol bigint) OWNER TO defaultxod;

--
-- Name: task_done(bigint); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.task_done(_id_task bigint) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set status = 'готово' where id_task = _id_task;
$$;


ALTER FUNCTION public.task_done(_id_task bigint) OWNER TO defaultxod;

--
-- Name: update_category(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.update_category(_id_category integer, _name character varying, _description character varying) RETURNS void
    LANGUAGE sql
    AS $$
	update category set name=_name, description = _description where id_category=_id_category;
$$;


ALTER FUNCTION public.update_category(_id_category integer, _name character varying, _description character varying) OWNER TO defaultxod;

--
-- Name: update_task(bigint, character varying, text); Type: FUNCTION; Schema: public; Owner: defaultxod
--

CREATE FUNCTION public.update_task(_id_task bigint, _name character varying, _description text) RETURNS void
    LANGUAGE sql
    AS $$
	update tasks set name=_name, description = _description where id_task = _id_task
$$;


ALTER FUNCTION public.update_task(_id_task bigint, _name character varying, _description text) OWNER TO defaultxod;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: category; Type: TABLE; Schema: public; Owner: defaultxod
--

CREATE TABLE public.category (
    id_category integer NOT NULL,
    name character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE public.category OWNER TO defaultxod;

--
-- Name: category_id_category_seq; Type: SEQUENCE; Schema: public; Owner: defaultxod
--

CREATE SEQUENCE public.category_id_category_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.category_id_category_seq OWNER TO defaultxod;

--
-- Name: category_id_category_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultxod
--

ALTER SEQUENCE public.category_id_category_seq OWNED BY public.category.id_category;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: defaultxod
--

CREATE TABLE public.tasks (
    id_task integer NOT NULL,
    id_desp bigint NOT NULL,
    id_vol bigint,
    id_category bigint NOT NULL,
    status character varying NOT NULL,
    name character varying NOT NULL,
    description text NOT NULL,
    expire_date date
);


ALTER TABLE public.tasks OWNER TO defaultxod;

--
-- Name: tasks_id_task_seq; Type: SEQUENCE; Schema: public; Owner: defaultxod
--

CREATE SEQUENCE public.tasks_id_task_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_task_seq OWNER TO defaultxod;

--
-- Name: tasks_id_task_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultxod
--

ALTER SEQUENCE public.tasks_id_task_seq OWNED BY public.tasks.id_task;


--
-- Name: user_types; Type: TABLE; Schema: public; Owner: defaultxod
--

CREATE TABLE public.user_types (
    id_user_type integer NOT NULL,
    user_type_name character varying(255) NOT NULL,
    ru_user_type_name character varying,
    regestration_allowed boolean
);


ALTER TABLE public.user_types OWNER TO defaultxod;

--
-- Name: user_types_id_user_type_seq; Type: SEQUENCE; Schema: public; Owner: defaultxod
--

CREATE SEQUENCE public.user_types_id_user_type_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_types_id_user_type_seq OWNER TO defaultxod;

--
-- Name: user_types_id_user_type_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultxod
--

ALTER SEQUENCE public.user_types_id_user_type_seq OWNED BY public.user_types.id_user_type;


--
-- Name: users; Type: TABLE; Schema: public; Owner: defaultxod
--

CREATE TABLE public.users (
    id_user bigint NOT NULL,
    id_user_type bigint,
    name character varying(255) NOT NULL,
    surname character varying(255) NOT NULL,
    address character varying(255) NOT NULL,
    phone bigint NOT NULL,
    contact_str character varying
);


ALTER TABLE public.users OWNER TO defaultxod;

--
-- Name: category id_category; Type: DEFAULT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.category ALTER COLUMN id_category SET DEFAULT nextval('public.category_id_category_seq'::regclass);


--
-- Name: tasks id_task; Type: DEFAULT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id_task SET DEFAULT nextval('public.tasks_id_task_seq'::regclass);


--
-- Name: user_types id_user_type; Type: DEFAULT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.user_types ALTER COLUMN id_user_type SET DEFAULT nextval('public.user_types_id_user_type_seq'::regclass);


--
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: defaultxod
--

COPY public.category (id_category, name, description) FROM stdin;
23	Еда и вода	Принос воды в труднодоступные места
5	Гуманитарная помощь	Волонтеры помогают, организовать сбор гуманитарных продуктов: продуктов питания, воды, одежды и так далее.
6	Помощь в приюте для животных	Волонтеры помогают в уходе за животными в местном приюте, включая кормление, уборку клеток, прогулки с собаками и общение с животными для их социализации.
7	Организация мероприятий для детей	Волонтеры организуют и проводят развлекательные мероприятия для детей из малообеспеченных семей, включая мастер-классы, спортивные соревнования и творческие занятия.
8	Работа с пожилыми людьми	Волонтеры оказывают помощь пожилым людям, живущим в одиночестве, выполняя различные поручения, такие как покупка продуктов, уборка дома, помощь в приготовлении пищи и просто общение.
9	Экологические проекты	Волонтеры участвуют в экологических акциях, таких как уборка парков и пляжей, посадка деревьев и кустарников, а также распространение информации о важности сохранения окружающей среды.
10	Поддержка культурных мероприятий	Волонтеры помогают в организации и проведении культурных мероприятий, таких как фестивали, выставки, концерты и спектакли, предоставляя свою помощь в различных аспектах, от продажи билетов до помощи на месте проведения.
11	Обучение и наставничество	Волонтеры занимаются обучением и наставничеством, помогая молодым людям и студентам в учебе, профессиональном развитии и личностном росте.
12	Медицинская помощь	Волонтеры оказывают медицинскую помощь, например, в качестве волонтеров в больницах, хосписах или в рамках программ по вакцинации.
13	Психологическая поддержка	Волонтеры предоставляют психологическую поддержку, например, через телефонные линии доверия, консультации или группы поддержки.
14	Информационные кампании	Волонтеры участвуют в информационных кампаниях, направленных на повышение осведомленности о важных социальных, экологических или медицинских вопросах.
15	Развитие сообщества	Волонтеры работают над развитием местных сообществ, организуя мероприятия, направленные на укрепление связей между жителями и создание благоприятной атмосферы.
16	Помощь в чрезвычайных ситуациях	Волонтеры оказывают помощь в случае стихийных бедствий, катастроф или других чрезвычайных ситуаций, участвуя в сборе и распределении гуманитарной помощи.
17	Помощь бездомным	Волонтеры помогают бездомным людям, предоставляя им еду, одежду, медицинскую помощь и поддержку в поиске жилья.
18	Помощь в реабилитации	Волонтеры помогают людям, проходящим реабилитацию после травм, болезней или зависимостей, предоставляя им поддержку и мотивацию.
20	Помощь в спорте	Волонтеры помогают организовывать спортивные мероприятия для молодежи и взрослых, предоставляя им возможность заниматься спортом и вести здоровый образ жизни.
21	Другое	Волонтеры помогают со всем, что не подходит ни в одну из категорий.
\.

--
-- Data for Name: user_types; Type: TABLE DATA; Schema: public; Owner: defaultxod
--

COPY public.user_types (id_user_type, user_type_name, ru_user_type_name, regestration_allowed) FROM stdin;
1	desp	нуждающийся	t
2	vol	волонтер	t
3	admin	админ	f
4	blocked	заблокированные	f
\.

--
-- Name: category_id_category_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultxod
--

SELECT pg_catalog.setval('public.category_id_category_seq', 23, true);


--
-- Name: tasks_id_task_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultxod
--

SELECT pg_catalog.setval('public.tasks_id_task_seq', 59, true);


--
-- Name: user_types_id_user_type_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultxod
--

SELECT pg_catalog.setval('public.user_types_id_user_type_seq', 4, true);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id_category);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id_task);


--
-- Name: user_types user_types_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_pkey PRIMARY KEY (id_user_type);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);


--
-- Name: tasks tasks_id_category_foreign; Type: FK CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_category_foreign FOREIGN KEY (id_category) REFERENCES public.category(id_category);


--
-- Name: tasks tasks_id_desp_foreign; Type: FK CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_desp_foreign FOREIGN KEY (id_desp) REFERENCES public.users(id_user);


--
-- Name: tasks tasks_id_vol_foreign; Type: FK CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_id_vol_foreign FOREIGN KEY (id_vol) REFERENCES public.users(id_user);


--
-- Name: users users_id_user_type_foreign; Type: FK CONSTRAINT; Schema: public; Owner: defaultxod
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_user_type_foreign FOREIGN KEY (id_user_type) REFERENCES public.user_types(id_user_type);


--
-- PostgreSQL database dump complete
--

