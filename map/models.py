
from django.contrib.gis.db import models


class KDK(models.Model):
    """
    KDK hydrological dataset.

    Contains all original attributes from KDK.dbf
    and geometries from KDK.shp.

    Coordinate reference system: EPSG:5514 (S-JTSK).
    """

    # Catchment identifiers
    fid_poviv = models.BigIntegerField(
        db_column="FID_PovIV",
        null=True,
        blank=True,
    )

    globalid = models.CharField(
        db_column="globalid",
        max_length=38,
        null=True,
        blank=True,
    )

    # Hydrological identifiers
    chp_4 = models.CharField(
        db_column="chp_4",
        max_length=17,
        null=True,
        blank=True,
        db_index=True,
    )

    chp_u = models.CharField(
        db_column="chp_u",
        max_length=12,
        null=True,
        blank=True,
    )

    chp_d = models.CharField(
        db_column="chp_d",
        max_length=12,
        null=True,
        blank=True,
    )

    # Watercourse names
    naz_tok = models.CharField(
        db_column="naz_tok",
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )

    naz_tok_2 = models.CharField(
        db_column="naz_tok_2",
        max_length=50,
        null=True,
        blank=True,
    )

    # Area attributes
    a_km2 = models.FloatField(
        db_column="a_km2",
        null=True,
        blank=True,
    )

    asum_km2 = models.FloatField(
        db_column="asum_km2",
        null=True,
        blank=True,
    )

    aa_km2 = models.FloatField(
        db_column="aa_km2",
        null=True,
        blank=True,
    )

    area = models.FloatField(
        db_column="Area",
        null=True,
        blank=True,
    )

    # KDK identifiers
    fid_kdk = models.BigIntegerField(
        db_column="FID_KDK",
        null=True,
        blank=True,
    )

    arcid = models.BigIntegerField(
        db_column="arcid",
        null=True,
        blank=True,
        db_index=True,
    )

    grid_code = models.BigIntegerField(
        db_column="grid_code",
        null=True,
        blank=True,
    )

    # Network topology
    from_node = models.BigIntegerField(
        db_column="from_node",
        null=True,
        blank=True,
    )

    to_node = models.BigIntegerField(
        db_column="to_node",
        null=True,
        blank=True,
    )

    # Additional attributes
    f_kdk = models.FloatField(
        db_column="F_KDK",
        null=True,
        blank=True,
    )

    shape_leng = models.FloatField(
        db_column="Shape_Leng",
        null=True,
        blank=True,
    )

    # Spatial geometry
    geom = models.MultiLineStringField(
        srid=5514,
        spatial_index=True,
    )

    class Meta:
        verbose_name = "KDK segment"
        verbose_name_plural = "KDK segments"

        indexes = [
            models.Index(
                fields=["fid_poviv"],
                name="kdk_fid_poviv_idx",
            ),
            models.Index(
                fields=["fid_kdk"],
                name="kdk_fid_kdk_idx",
            ),
            models.Index(
                fields=["from_node", "to_node"],
                name="kdk_nodes_idx",
            ),
        ]

    def __str__(self):
        return f"{self.naz_tok or 'Unnamed'} ({self.pk})"
