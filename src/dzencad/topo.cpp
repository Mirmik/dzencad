#include <dzencad/topo.h>
#include <dzencad/trans.h>
#include <dzencad/boolops.h>
//#include <gxx/print.h>

std::shared_ptr<DzenShape> DzenShape::transform(std::shared_ptr<DzenTransform> trsf) {
	return std::shared_ptr<DzenShape>(new DzenTransformShape(get_spointer(), trsf));
}

std::shared_ptr<DzenShape> DzenShape::translate(double x, double y, double z) {
	return transform(std::shared_ptr<DzenTransform>(new DzenTranslate(x, y, z)));
}

std::shared_ptr<DzenShape> DzenShape::up(double z) {
	return translate(0,0,z);
}

std::shared_ptr<DzenShape> DzenShape::down(double z) {
	return translate(0,0,-z);
}

std::shared_ptr<DzenShape> DzenShape::right(double x) {
	return translate(x,0,0);
}

std::shared_ptr<DzenShape> DzenShape::left(double x) {
	return translate(-x,0,0);
}

std::shared_ptr<DzenShape> DzenShape::forw(double y) {
	return translate(0,y,0);
}

std::shared_ptr<DzenShape> DzenShape::back(double y) {
	return translate(0,-y,0);
}


std::shared_ptr<DzenShape> DzenShape::rotateX(double a) {
	return std::shared_ptr<DzenShape>(new DzenTransformShape(get_spointer(), trans_rotateX(a)));
}

std::shared_ptr<DzenShape> DzenShape::rotateY(double a) {
	return std::shared_ptr<DzenShape>(new DzenTransformShape(get_spointer(), trans_rotateY(a)));
}

std::shared_ptr<DzenShape> DzenShape::rotateZ(double a) {
	return std::shared_ptr<DzenShape>(new DzenTransformShape(get_spointer(), trans_rotateZ(a)));
}



std::shared_ptr<DzenShape> operator+ (const DzenShape& lhs, const DzenShape& rhs) {
	return std::shared_ptr<DzenShape>(new DzenUnion(lhs.get_spointer(), rhs.get_spointer()));
}

std::shared_ptr<DzenShape> operator- (const DzenShape& lhs, const DzenShape& rhs) {
	return std::shared_ptr<DzenShape>(new DzenDifference(lhs.get_spointer(), rhs.get_spointer()));
}

std::shared_ptr<DzenShape> operator^ (const DzenShape& lhs, const DzenShape& rhs) {
	return std::shared_ptr<DzenShape>(new DzenIntersect(lhs.get_spointer(), rhs.get_spointer()));
}

std::shared_ptr<DzenShape> DzenShape::get_spointer() const {
	return std::dynamic_pointer_cast<DzenShape, DzenCadObject>((const_cast<DzenShape*>(this))->shared_from_this());
}