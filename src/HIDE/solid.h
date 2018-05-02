#ifndef DZENCAD_SOLID_H
#define DZENCAD_SOLID_H

#include <zencad/topo.h>
#include <zencad/math3.h>
#include <memory>

#include <pybind11/pybind11.h>

namespace py = pybind11;

struct ZenSolid : public ZenShape, public ZenShapeTransI<ZenSolid>, public ZenBoolOpsI<ZenSolid> {
	const char* class_name() const { return "ZenSolid"; }

	std::shared_ptr<ZenSolid> spointer() const {
		ZenSolid* self = const_cast<ZenSolid*>(this);
		return std::dynamic_pointer_cast<ZenSolid,ZenCadObject>(self->shared_from_this());
	}
};

struct ZenBox : public ZenSolid {
	const char* class_name() const override;
	double x, y, z;
	bool center = false;
	ZenBox(double x, double y, double z, bool center);
	//ZenBox(double x, double y, double z, py::kwargs kw);
	void doit() override;
	void vreflect(ZenVisitor& v) override;
};

struct ZenSphere : public ZenSolid {
	const char* class_name() const override;
	double r;
	ZenSphere(double r);
	void doit() override;
	void vreflect(ZenVisitor& v) override;
};

struct ZenCylinder : public ZenSolid {
	const char* class_name() const override;
	double r, h;
	bool center = false;
	ZenCylinder(double r, double h, bool center);
	void doit() override;
	void vreflect(ZenVisitor& v) override;
};

struct ZenTorus : public ZenSolid {
	const char* class_name() const override;
	double r1, r2;
	ZenTorus(double r1, double r2);
	void doit() override;
	void vreflect(ZenVisitor& v) override;
};

struct ZenCone : public ZenSolid {
	const char* class_name() const override;
	double r1, r2, h;
	bool center;
	ZenCone(double r1, double r2, double h, bool center);
	void doit() override;
	void vreflect(ZenVisitor& v) override;	
};

/*
struct ZenWedge : public ZenSolid {
	const char* class_name() const override;
	double x, y, z, ltx;
	ZenWedge(double x, double y, double z, double ltx);
	void doit() override;
};
*/

struct ZenLinearExtrude : public ZenSolid {
	const char* class_name() const override;
	ZenVector3 vec;
	std::shared_ptr<ZenFace> fc;
	ZenLinearExtrude(std::shared_ptr<ZenFace> fc, double z);
	ZenLinearExtrude(std::shared_ptr<ZenFace> fc, ZenVector3 v);
	void doit() override;
	void vreflect(ZenVisitor& v) override;	
};

struct ZenPipe : public ZenSolid {
	const char* class_name() const override;
	//ZenVector3 vec;
	std::shared_ptr<ZenWire> path;
	std::shared_ptr<ZenShape> profile;
	ZenPipe(std::shared_ptr<ZenWire> path, std::shared_ptr<ZenShape> profile);
	void doit() override;
	void vreflect(ZenVisitor& v) override;	
};

/*
struct ZenLoft : public ZenSolid {
	const char* class_name() const override;
	std::vector<std::shared_ptr<ZenShape>> shapes;
	ZenLoft(pybind11::list args);
	void doit() override;
};
*/
/*
struct ZenPipe : public ZenSolid {
	const char* class_name() const override;
	std::shared_ptr<ZenWire> path;
	std::shared_ptr<ZenShape> profile;
	ZenPipe(std::shared_ptr<ZenWire> path, std::shared_ptr<ZenShape> profile);
	void doit() override;
};
*/
#endif