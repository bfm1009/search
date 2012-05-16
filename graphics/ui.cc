#include "ui.hpp"
#include "../utils/utils.hpp"
#include <cstdio>
#include <SDL/SDL.h>
#include <SDL/SDL_image.h>
#include <SDL/SDL_opengl.h>

Ui::Ui(unsigned int w, unsigned int h) : scene(w, h) {
	if (SDL_Init(SDL_INIT_EVERYTHING) != 0)
		fatal("failed to initialiaze SDL: %s", SDL_GetError());

	int flags = IMG_INIT_PNG;
	int inited = IMG_Init(flags);
	if ((inited & flags) != flags)
		fatal("Failed to initialize .png support");

	flags = SDL_GL_DOUBLEBUFFER | SDL_OPENGL;
	unsigned int color = 32;
	screen = SDL_SetVideoMode(scene.width, scene.height, color, flags);
	if (!screen)
		fatal("failed to create a window: %s", SDL_GetError());

	fprintf(stderr, "Vendor: %s\nRenderer: %s\nVersion: %s\nShade Lang. Version: %s\n",
		glGetString(GL_VENDOR),
		glGetString(GL_RENDERER),
		glGetString(GL_VERSION),
		glGetString(GL_SHADING_LANGUAGE_VERSION));


	glDisable(GL_DEPTH_TEST);
	glEnable(GL_POINT_SMOOTH);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

	glTranslated(-1.0, -1.0, 0.0);
	glScaled(2.0 / scene.width, 2.0 / scene.height, 0.0);
	glClearColor(1.0, 1.0, 1.0, 0.0);
	chkerror("after initialization");
}

void Ui::run(unsigned long rate) {
	for ( ; ; ) {
		long tick = SDL_GetTicks();

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		frame();
		scene.render();
		glFlush();
		SDL_GL_SwapBuffers();
		chkerror("after swap buffers");

		if (handleevents())
			break;

		long delay = tick + rate - SDL_GetTicks();
		if (delay > 0)
			SDL_Delay(delay);
	}
}

void Ui::chkerror(const char *str) {
	GLenum err = glGetError();
	switch (err) {
	case GL_NO_ERROR:
		break;

	case GL_INVALID_ENUM:
		fatal("GL error %s: GL_INVALID_ENUM (%d)", str, err);

	case GL_INVALID_VALUE:
		fatal("GL error %s: GL_INVALID_VALUE (%d)", str, err);

	case GL_INVALID_OPERATION:
		fatal("GL error %s: GL_INVALID_OPERATION (%d)", str, err);

	case GL_STACK_OVERFLOW:
		fatal("GL error %s: GL_STACK_OVERFLOW (%d)", str, err);

	case GL_STACK_UNDERFLOW:
		fatal("GL error %s: GL_STACK_UNDERFLOW (%d)", str, err);

	case GL_OUT_OF_MEMORY:
		fatal("GL error %s: GL_OUT_OF_MEMORY (%d)", str, err);

	case GL_TABLE_TOO_LARGE:
		fatal("GL error %s: GL_TABLE_TOO_LARGE (%d)", str, err);

	default:
		fatal("Unknow GL error %s: %d\n", err);
	}
}

bool Ui::handleevents() {
	for ( ; ; ) {
		SDL_Event e;
		int p = SDL_PollEvent(&e);
		if (!p)
			break;

		switch(e.type) {
		case SDL_QUIT:
			return true;
		case SDL_KEYDOWN:
			key(e.key.keysym.sym, true);
			break;
		case SDL_KEYUP:
			key(e.key.keysym.sym, false);
			break;
		case SDL_MOUSEMOTION:
			motion(e.motion.x, e.motion.y, e.motion.xrel, e.motion.yrel);
			break;
		case SDL_MOUSEBUTTONDOWN:
			click(e.button.x, e.button.y, e.button.button, true);
			break;
		case SDL_MOUSEBUTTONUP:
			click(e.button.x, e.button.y, e.button.button, false);
			break;
		default:
			break;
		}
	}
	return false;
}

void Ui::frame() {
	scene.clear();
	geom2d::Pt center(scene.width / 2, scene.height / 2);

	unsigned int color = 0;

	geom2d::Poly p = geom2d::Poly::random(10, 0, 0, 1);
	p.scale(scene.width / 2, scene.height / 2);
	p.translate(scene.width / 2, scene.height / 2);
	scene.add(new Scene::Poly(p, somecolors[color++ % Nsomecolors], 1));

	geom2d::Arc a = geom2d::Arc(center, scene.width / 10, 0, M_PI);
	scene.add(new Scene::Arc(a, somecolors[color++ % Nsomecolors], 1));

	scene.add(new Scene::Pt(geom2d::Pt(0.0, 0.0), Image::blue, 10, 1));
	scene.add(new Scene::Pt(geom2d::Pt(scene.width, scene.height), Image::green, 10, 1));
}

void Ui::key(int key, bool down) {
	printf("key %d %s\n", key, down ? "down" : "up");
}

void Ui::motion(int x, int y, int dx, int dy) {
	printf("mouse motion: (%d, %d) delta=(%d, %d)\n", x, y, dx, dy);
}

void Ui::click(int x ,int y, int button, bool down) {
	printf("mouse click: button %d at (%d, %d) %s\n", button, x, y, down ? "down" : "up");
}