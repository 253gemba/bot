import asyncio

from utils.amo.methods import Contact, Lead


async def check_leads(c, conn, leads):
    for lead in leads:
        lead: Lead
        deal_id = lead.id
        city = lead.city
        budget = lead.price
        address = lead.address
        service = lead.service
        start_datetime = lead.start_datetime
        count_loaders = lead.count_loaders
        car_type = lead.car_type
        minimum = lead.minimum
        floor_descent = lead.floor_descent
        floor_rise = lead.floor_rise
        rigging = lead.rigging
        add_service = lead.add_service
        note = lead.note
        contacts = lead.contacts
        responsible_user = lead.responsible_user.name
        area_price = lead.area_price
        min_auto = lead.min_auto
        add_hour = lead.add_hour
        add_hour = add_hour if str(add_hour).isdigit() else 0
        paid_for_km = lead.paid_for_km
        phone = None
        print(lead.status)
        await asyncio.sleep(0)
        if lead.status.id == 34302931:
            print(lead)
            for contact in contacts:
                contact: Contact
                contacts_by_id = Contact.objects.get(object_id=contact.id)
                phone = contacts_by_id.phone
                await asyncio.sleep(0)
            c.execute("select count(*) from amo_deals where deal_id = %s", (deal_id,))
            add_service = [] if not add_service else add_service
            add_service = [x.value for x in add_service]
            add_service = "; ".join(add_service)
            print(city, address, service, start_datetime, count_loaders, car_type, minimum, floor_rise,
                  floor_descent, rigging, add_service, note, responsible_user, phone, area_price)
            if not c.fetchone()[0]:
                await asyncio.sleep(0)
                c.execute("insert into amo_deals (deal_id, city, address, service, start_datetime, count_loaders, "
                          "car_type, minimum, floor_descent, floor_rise, rigging, add_service, note, phone, "
                          "responsible_user, budget, area_price, min_auto, add_hour, paid_for_km) "
                          "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                          (deal_id, city, address, service, start_datetime, count_loaders, car_type, minimum,
                           floor_descent, floor_rise, rigging, add_service, note, phone, responsible_user, budget,
                           area_price, min_auto, add_hour, paid_for_km))
                conn.commit()
            else:
                c.execute(
                    "select city, address, service, start_datetime, count_loaders, car_type, minimum, "
                    "floor_descent, floor_rise, rigging, add_service, note, phone, budget, area_price "
                    "from amo_deals where deal_id = %s", (deal_id,))
                old_city, old_address, old_service, old_start_datetime, old_count_loaders, old_car_type, \
                old_minimum, old_floor_descent, old_floor_rise, old_rigging, old_add_service, old_note, old_phone, \
                old_budget, old_area_price = c.fetchone()
                await asyncio.sleep(0)
                if city != old_city or address != old_address or service != old_service or \
                        old_start_datetime != start_datetime or old_count_loaders != count_loaders or \
                        old_car_type != car_type or minimum != old_minimum or floor_descent != old_floor_descent or \
                        floor_rise != old_floor_rise or rigging != old_rigging or old_add_service != add_service or \
                        note != old_note or phone != old_phone or budget != old_budget or area_price != old_area_price:
                    c.execute("update amo_deals set city = %s, address = %s, service = %s, start_datetime = %s, "
                              "count_loaders = %s, car_type = %s, minimum = %s, floor_descent = %s, floor_rise = %s, "
                              "rigging = %s, add_service = %s, note = %s, phone = %s, budget = %s, edit_push = 0, "
                              "edit_address = %s, edit_budget = %s, edit_city = %s, edit_minimum = %s, "
                              "edit_phone = %s, edit_service = %s, edit_start_datetime = %s, area_price = %s "
                              "where deal_id = %s",
                              (city, address, service, start_datetime, count_loaders, car_type, minimum,
                               floor_descent, floor_rise, rigging, add_service, note, phone, budget,
                               address != old_address, budget != old_budget, city != old_city, minimum != old_minimum,
                               phone != old_phone, service != old_service, old_start_datetime != start_datetime,
                               area_price, deal_id))
                    conn.commit()
                else:
                    c.execute("select count(*) from amo_deals "
                              "where deal_id = %s and is_active = 0 and active_push = 1", (deal_id,))
                    if c.fetchone()[0]:
                        await asyncio.sleep(0)
                        c.execute("update amo_deals set is_active = 1, active_push = 0 where deal_id = %s",
                                  (deal_id,))
                        conn.commit()
        await asyncio.sleep(1)


async def check_rejected(c, conn, leads_rejected):
    for lead in leads_rejected:
        deal_id = lead.id
        print(lead.status)
        if lead.status.id in (34386043, 143):
            print(lead)
            c.execute("select count(*) from amo_deals "
                      "where deal_id = %s and is_active = 1 and active_push = 1", (deal_id,))
            if c.fetchone()[0]:
                await asyncio.sleep(0)
                c.execute("update amo_deals set is_active = 0, active_push = 0 where deal_id = %s", (deal_id,))
                conn.commit()
        await asyncio.sleep(1)
